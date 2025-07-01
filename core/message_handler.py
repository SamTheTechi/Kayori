import json
from datetime import datetime, timedelta, timezone
from services.redis_db import redis_client, MESSAGE_QUEUE, MESSAGE_SET
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from core.analyse_mood import analyse_mood
from util.stream_and_handle_response import stream_and_handle_response
from util.chunker import split_text
from util.get_current_time import get_current_time
from services.state_store import get_mood


async def message_handler(client, private_executer, public_executer, vector_store, USER_ID):
    while True:
        try:
            # Wait for a new message payload from Redis queue
            raw_data = await redis_client.brpop(MESSAGE_QUEUE)
            if not raw_data:
                continue

            _, raw_message = raw_data
            data = json.loads(raw_message)

            # Extract message metadata
            author_id = data.get("author_id")
            is_dm = data.get("is_dm", False)

            # Fetch Discord objects
            author = await client.fetch_user(author_id)
            target_user = await client.fetch_user(USER_ID)

            if is_dm and target_user == author:
                await handle_direct_message(client, private_executer, vector_store, data)
            else:
                await handle_server_message(client, public_executer, vector_store, data)

        except Exception as e:
            print(f"error: {e}")


async def handle_direct_message(client, executer, vector_store, data):
    user_input = data.get("content", "")
    thread_id = str(data.get("channel_id"))
    config = {"configurable": {"thread_id": thread_id}}

    message_id = data.get("message_id")
    channel_id = data.get("channel_id")
    author_id = data.get("author_id")

    channel = await client.fetch_channel(channel_id)
    author = await client.fetch_user(author_id)
    original_message = await channel.fetch_message(message_id)

    await author.typing()

    docs = vector_store.similarity_search(query=user_input, k=2)

    context = [
        SystemMessage(content="Here is relevant context from previous interactions to help you respond accurately"),
        *[AIMessage(content=f"{doc.page_content}") for doc in docs]
    ]
    val = context + [HumanMessage(user_input)]

    reaction = await analyse_mood(user_input)
    if reaction.strip():
        await original_message.add_reaction(reaction)

    natures = await get_mood()
    llm_payload = {
        "messages": val,
        "Affection": str(natures["Affection"]),
        "Amused": str(natures["Amused"]),
        "Inspired": str(natures["Inspired"]),
        "Frustrated": str(natures["Frustrated"]),
        "Concerned": str(natures["Concerned"]),
        "Curious": str(natures["Curious"]),
        "current_time": str(get_current_time())
    }

    final_text = await stream_and_handle_response(executer, llm_payload, config, author)

    if final_text.strip():
        chunkted = split_text(final_text)
        vector_store.add_documents([Document(chunk) for chunk in chunkted])


async def handle_server_message(client, executer, vector_store, data):
    active_user_count = await redis_client.scard(MESSAGE_SET)

    thread_id = str(data.get("channel_id"))
    config = {"configurable": {"thread_id": thread_id}}

    message_id = data.get("message_id")
    channel_id = data.get("channel_id")
    author_id = data.get("author_id")
    user_input = data.get("content", "")

    channel = await client.fetch_channel(channel_id)
    author = await client.fetch_user(author_id)
    original_message = await channel.fetch_message(message_id)

    await channel.typing()

    chat_history = await get_chat_history(channel, client.user.id)

    # Retrieve relevant past context from her memory (vector_store)
    docs = vector_store.similarity_search(query=user_input, k=2)
    chat_history.reverse()

    context = [
        SystemMessage(content="Relevant memories with sam retrieved from earlier interactions"),
        *[AIMessage(content=f"{doc.page_content}") for doc in docs],
        SystemMessage(content="Here is the current group conversation"),
        *chat_history,
        HumanMessage(
            content=user_input,
            additional_kwargs={
                "role": author.display_name,
                "source": "live_input"
            }
        )
    ]

    # React to message based on tone
    reaction = await analyse_mood(user_input)
    if reaction.strip():
        await original_message.add_reaction(reaction)

    # Current mood values
    natures = await get_mood()
    llm_payload = {
        "messages": context,
        "Affection": str(natures["Affection"]),
        "Amused": str(natures["Amused"]),
        "Inspired": str(natures["Inspired"]),
        "Frustrated": str(natures["Frustrated"]),
        "Concerned": str(natures["Concerned"]),
        "Curious": str(natures["Curious"]),
        "replying_to": str(author.display_name),
        "current_time": str(get_current_time())
    }

    await stream_and_handle_response(executer, llm_payload, config, original_message, reply=active_user_count > 1)

    # removes item to set
    await redis_client.srem(MESSAGE_SET, f"{data.get('author_id')}:{data.get('channel_id')}")


async def get_chat_history(channel, bot_id):
    chat_history = []
    skip_first = True

    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=30)

    async for msg in channel.history(limit=15, oldest_first=False):

        if skip_first:
            skip_first = False
            continue

        if msg.created_at < cutoff_time:
            continue

        if msg.content and len(msg.content.strip()) > 3 and not msg.content.strip().startswith(("/", "!")):
            if msg.author.id == bot_id:
                chat_history.append(AIMessage(content=f'{msg.content}'))
            else:
                chat_history.append(HumanMessage(
                    content=msg.content.strip(),
                    name=msg.author.display_name.lower().replace(" ", "_"),
                    additional_kwargs={"role": f"{msg.author.display_name}", "source": "past conversation"})
                )
    return chat_history
