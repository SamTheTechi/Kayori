import discord
import random
import pytz
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from util.reaction import analyseNature
from util.store import natures, update_context, get_context, update_last_time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from scheduling.adaptive_scheduler import weather
from scheduling.locations import location_change
from scheduling.nature import change_pfp, mood_drift, mood_spike
from scheduling.greetings import good_evening, good_morning


def setup_discord_bot(agent_executer, vector_store, config):
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)
    scheduler = AsyncIOScheduler()

    current_time = datetime.now(pytz.utc).astimezone(
        pytz.timezone("Asia/Kolkata")
    ).strftime('%Y-%m-%d  %H:%M')

    @client.event
    async def on_ready():
        try:

            # Schedule periodic profile picture changes
            scheduler.add_job(change_pfp, "interval",
                              hours=random.randint(17, 20), args=[client])

            # Schedule morning and evening greetings
            scheduler.add_job(good_morning, "cron", hour=random.randint(
                7, 9), args=[client, agent_executer, config])
            scheduler.add_job(good_evening, "cron", hour=random.randint(
                17, 19), args=[client, agent_executer, config])

            # Schedule mood updates
            scheduler.add_job(mood_drift, "interval",
                              minutes=random.randint(4, 7))
            scheduler.add_job(mood_spike, "interval",
                              minutes=random.randint(50, 60))

            # Schedule weather and location updates
            scheduler.add_job(weather, "interval", hours=random.randint(
                14, 16), args=[client, agent_executer, config])
            scheduler.add_job(location_change, "interval", minutes=30, args=[
                              client, agent_executer, config, vector_store])

            print(f"Kaori is online as {client.user}")
            scheduler.start()
        except Exception as e:
            print(f"error: {e}")

    @client.event
    async def on_message(message):

        if message.author == client.user or not isinstance(
                message.channel, discord.DMChannel):
            return

        user_input = message.content
        response_text = ""
        final_text = ""
        tool_called = False

        # Retrieve relevant past interactions
        docs = vector_store.similarity_search(query=user_input, k=2)

        context = [
            SystemMessage(
                content="Here is relevant context from previous interactions to help you respond accurately"),
            *[AIMessage(content=f"{doc.page_content}") for doc in docs]
        ]

        val = context + [HumanMessage(user_input)]
        # val = [HumanMessage(user_input)]

        reaction = await analyseNature(user_input, get_context, natures)
        if reaction.strip() != "":
            await message.add_reaction(reaction)

        async with message.channel.typing():
            async for chunk in agent_executer.astream(
                {"messages": val,
                 "Affection": str(natures["Affection"]),
                 "Amused": str(natures["Amused"]),
                 "Inspired": str(natures["Inspired"]),
                 "Frustrated": str(natures["Frustrated"]),
                 "Concerned": str(natures["Concerned"]),
                 "Curious": str(natures["Curious"]),
                 "Current_time": str(current_time)
                 },
                config,
                stream_mode="updates",
            ):
                if 'agent' in chunk:
                    messages = chunk['agent'].get('messages', [])
                    for msg in messages:
                        if isinstance(msg, AIMessage):
                            if msg.tool_calls:
                                tool_called = True

                            if tool_called:
                                if response_text.strip():
                                    await message.author.send(response_text)
                                    final_text = response_text
                                    response_text = ""

                                response_text += msg.content
                            else:
                                response_text += msg.content

                if response_text.strip():
                    await message.author.send(response_text)
                    final_text += response_text
                    update_context(response_text)
                    update_last_time()

            if final_text.strip() and not tool_called:
                print("something")
                # chunkted = split_text(final_text)
                # vector_store.add_documents(
                #     [Documents(chunk) for chunk in chunkted])

    return client
