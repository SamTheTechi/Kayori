import json
from services.redis_db import redis_client, MESSAGE_QUEUE, MESSAGE_SET
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from util.reaction import analyseNature
from util.store import natures, update_context, get_context
from util.get_current_time import get_current_time


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
            message_id = data.get("message_id")
            channel_id = data.get("channel_id")
            author_id = data.get("author_id")
            content = data.get("content", "")
            is_dm = data.get("is_dm", False)

            # Fetch Discord objects
            channel = await client.fetch_channel(channel_id)
            author = await client.fetch_user(author_id)
            original_message = await channel.fetch_message(message_id)
            target_user = await client.fetch_user(USER_ID)

            # Setup for response building
            user_input = content
            final_text = ""
            response_text = ""
            tool_called = False

            thread_id = str(channel_id) if not is_dm else str(USER_ID)
            config = {"configurable": {"thread_id": thread_id}}

            # Handle DM from target user
            if is_dm and target_user == author:
                await author.typing()

                # Semantic vector context search
                docs = vector_store.similarity_search(query=user_input, k=2)

                # Build system and memory context for the model
                context = [
                    SystemMessage(content="Here is relevant context from previous interactions to help you respond accurately"),
                    *[AIMessage(content=f"{doc.page_content}") for doc in docs]
                ]
                val = context + [HumanMessage(user_input)]

                # Analyze user's tone and react
                reaction = await analyseNature(user_input, get_context, natures)
                if reaction.strip():
                    await original_message.add_reaction(reaction)

                # Stream model response
                async for chunk in private_executer.astream(
                    {
                        "messages": val,
                        "Affection": str(natures["Affection"]),
                        "Amused": str(natures["Amused"]),
                        "Inspired": str(natures["Inspired"]),
                        "Frustrated": str(natures["Frustrated"]),
                        "Concerned": str(natures["Concerned"]),
                        "Curious": str(natures["Curious"]),
                        "current_time": str(get_current_time())
                    },
                    config,
                    stream_mode="updates",
                ):
                    if 'agent' in chunk:
                        messages = chunk['agent'].get('messages', [])
                        for msg in messages:
                            if isinstance(msg, AIMessage):
                                if msg.content:
                                    response_text += msg.content

                                # Send reply if a tool is about to be called
                                if msg.tool_calls and not tool_called:
                                    print("tool called")
                                    tool_called = True
                                    if response_text.strip():
                                        await author.send(response_text)
                                        final_text += response_text
                                        response_text = ""

                # Send any remaining response
                if response_text.strip():
                    await author.send(response_text)
                    final_text += response_text
                    update_context(response_text)

                if final_text.strip() and not tool_called:
                    print("handled user")

                # chunkted = split_text(final_text)
                # vector_store.add_documents([Documents(chunk) for chunk in chunkted])

            # ----------- Handle Public Messages -----------
            else:
                active_user_count = await redis_client.scard(MESSAGE_SET)
                await channel.typing()

                # Retrieve others execluding user and kayori last chats messages in group chat
                chat_history = []
                skip_first = True

                async for msg in channel.history(limit=15, oldest_first=False):

                    # removing the msg which triggerd the kayori
                    if skip_first:
                        skip_first = False
                        continue

                    if msg.content and len(msg.content.strip()) > 3 and not msg.content.strip().startswith(("/", "!")):
                        if msg.author.id == USER_ID:
                            # Message from Kayori (your bot)
                            chat_history.append(AIMessage(content=f'{msg.author.display_name}: {msg.content}'))
                        else:
                            # Message from a user
                            chat_history.append(HumanMessage(content=f'{msg.author.display_name}: {msg.content}'))

                # Retrieve relevant past context from her memory (vector_store)
                docs = vector_store.similarity_search(query=user_input, k=2)
                chat_history.reverse()

                context = [
                    SystemMessage(content="Relevant memories with sam retrieved from earlier interactions:"),
                    *[AIMessage(content=f"{doc.page_content}") for doc in docs],

                    SystemMessage(content="Here is the current group conversation:"),
                    *chat_history,

                    HumanMessage(content=f"{author.display_name}: {user_input}")
                ]

                # React to message based on tone
                reaction = await analyseNature(user_input, get_context, natures)
                if reaction.strip():
                    await original_message.add_reaction(reaction)

                # Stream response from public LLM agent
                async for chunk in public_executer.astream(
                    {
                        "messages": context,
                        "Affection": str(natures["Affection"]),
                        "Amused": str(natures["Amused"]),
                        "Inspired": str(natures["Inspired"]),
                        "Frustrated": str(natures["Frustrated"]),
                        "Concerned": str(natures["Concerned"]),
                        "Curious": str(natures["Curious"]),
                        "replying_to": str(author.display_name),
                        "current_time": str(get_current_time())
                    },
                    config,
                    stream_mode="updates",
                ):
                    if 'agent' in chunk:
                        messages = chunk['agent'].get('messages', [])
                        for msg in messages:
                            if isinstance(msg, AIMessage):
                                if msg.content:
                                    response_text += msg.content

                                # Send message early if tool is triggered
                                if msg.tool_calls and not tool_called:
                                    tool_called = True
                                    if response_text.strip():
                                        if active_user_count > 1:
                                            await original_message.reply(response_text, mention_author=True)
                                        else:
                                            await channel.send(response_text)
                                        final_text += response_text
                                        response_text = ""

                # Send final remaining reply if any
                if response_text.strip():
                    if active_user_count > 1:
                        await original_message.reply(response_text, mention_author=True)
                    else:
                        await channel.send(response_text)

                    final_text += response_text
                    update_context(response_text)
                    print("server user")

                # removes item to set
                await redis_client.srem(MESSAGE_SET, f"{author_id}:{channel_id}")

        except Exception as e:
            print(f"error: {e}")
