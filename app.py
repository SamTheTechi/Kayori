import os
import random
import discord
import asyncio
from server import run_server
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from util.reaction import analyseNature
from services.vector_db import initalise_vector_db
from scheduling.adaptive_scheduler import (
    weather,
    location_change
)
from scheduling.time_scheduler import (
    change_pfp,
    good_evening,
    good_morning,
    mood_drift,
    mood_spike
)
from core.agent_executer import create_agent_executer
from util.store import natures, update_context, get_context, update_last_time
from util.chunker import split_text
from util.document import memory_constructor
from tools.spt import SpotifyTool
from tools.calender import CalenderAgentTool
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage
)
load_dotenv()
os.getenv("TAVILY_API_KEY")

# Neccessary initials

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.6,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    },
)
# ChatModel Persona: Kaori's defined personality

vector_store = initalise_vector_db()

# Tools available for Kaori
tavily = TavilySearchResults(max_results=2)
spotify = SpotifyTool()
calender = CalenderAgentTool()
tool = [spotify, tavily, calender]

agent_executer = create_agent_executer(llm, tool)

config = {"configurable": {"thread_id": "sameer"}}
#
# Discord bot setup
scheduler = AsyncIOScheduler()


@client.event
async def on_ready():
    # Schedule periodic profile picture changes
    try:
        scheduler.add_job(change_pfp, "interval",
                          hours=random.randint(17, 20), args=[client])

        # Schedule morning and evening greetings
        scheduler.add_job(good_morning, "cron", hour=random.randint(
            7, 9), args=[client, agent_executer, config])
        scheduler.add_job(good_evening, "cron", hour=random.randint(17, 19), args=[
                          client, agent_executer, config])

        # Schedule mood updates
        scheduler.add_job(mood_drift, "interval", minutes=random.randint(4, 7))
        scheduler.add_job(mood_spike, "interval",
                          minutes=random.randint(50, 60))

        # Schedule weather and location updates
        scheduler.add_job(weather, "interval", hours=random.randint(14, 16), args=[
                          client, agent_executer, config])
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
            chunkted = split_text(final_text)
            vector_store.add_documents(
                [memory_constructor(chunk) for chunk in chunkted])


async def main():
    bot_task = asyncio.create_task(client.start(TOKEN))
    api_task = asyncio.create_task(run_server())

    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
