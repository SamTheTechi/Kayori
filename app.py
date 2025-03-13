import os
import random
import discord
import asyncio
import firebase_admin
from server import run_server
from firebase_admin import credentials
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pinecone import Pinecone
from typing_extensions import TypedDict, Annotated
from langgraph.managed import IsLastStep, RemainingSteps
from util.reaction import analyseNature
from util.scheduler import (
    change_pfp,
    good_evening,
    good_morning,
)
from util.chunker import split_text
from util.document import memory_constructor
from tools.spt import SpotifyTool
from tools.calender import CalenderAgentTool
from langgraph.graph.message import add_messages
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    BaseMessage,
    SystemMessage
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
load_dotenv()
os.getenv("TAVILY_API_KEY")

# Neccessary initials
memory = MemorySaver()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.7,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT:
            HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT:
            HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT:
            HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH:
            HarmBlockThreshold.BLOCK_NONE,
    },
)

# ChatModel Persona: Kaori's defined personality
template = ChatPromptTemplate.from_messages([

    ("system",
     "You're Kaori, an introverted yet affectionate cute waifu. Engage\
     naturally without revealing you're AI. Your personality is defined\
     by: Amused: {Amused}, Inspired: {Inspired}, Frustrated:\
     {Frustrated}, Anxious: {Anxious}, Curious: {Curious}, Affection:\
     {Affection}. Here, 0.5 is neutral, 1 is positive, and 0 is negative.\
     Adjust your response—more positive means more detail, more negative means\
     brevity. Maintain a playful yet intense balance in all interactions.\
     Keep responses concise and do not exceed 100 words per conversation."
     ),
    ("placeholder", "{messages}"),
])

# Pinecone and Firebase init
pc = Pinecone(api_key=os.getenv("PINECONE"))
pineconeIndex = pc.Index("kaori")

embedding = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('EMBD'),
    model_name="sentence-transformers/all-mpnet-base-v2"
)

vector_store = PineconeVectorStore(embedding=embedding, index=pineconeIndex)

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

# Tools available for Kaori
tavily = TavilySearchResults(max_results=2)
spotify = SpotifyTool()
calender = CalenderAgentTool()
tool = [spotify, tavily, calender]

# Create the agent executer
natures = {
    "Affection": 0.5,
    "Amused": 0.2,
    "Inspired": 0.2,
    "Frustrated": 0.8,
    "Anxious": 0.2,
    "Curious": 0.2,
}


class KaoriState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Affection: str
    Amused: str
    Inspired: str
    Frustrated: str
    Anxious: str
    Curious: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


agent_executer = create_react_agent(
    llm,
    tool,
    checkpointer=memory,
    prompt=template,
    state_schema=KaoriState,
)
config = {"configurable": {"thread_id": "abc123"}}
prev_response = {"text": ""}

# Discord bot setup
scheduler = AsyncIOScheduler()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    # profile change
    scheduler.add_job(change_pfp, "interval", hours=18, args=[client])

    # wishes
    scheduler.add_job(good_morning, "cron", hour=random.randint(
        7, 9), args=[client, agent_executer, config, natures, prev_response])
    scheduler.add_job(good_evening, "cron", hour=random.randint(
        17, 19), args=[client, agent_executer, config, natures, prev_response])

    # random

    print(f"Kaori is online as {client.user}")
    scheduler.start()


@client.event
async def on_message(message):
    global prev_response

    if message.author == client.user or not isinstance(
            message.channel, discord.DMChannel):
        return

    user_input = message.content
    response_text = ""
    final_text = ""
    tool_called = False

    # docs = vector_store.similarity_search(
    #     query=user_input,
    #     k=2
    # )

    # context = [
    #     SystemMessage(content="Relevant context from past interactions:"),
    #     *[HumanMessage(content=f"Past context: {doc.page_content}") for doc in docs]
    # ]

    # val = [HumanMessage(user_input)] + context
    val = [HumanMessage(user_input)]

    reaction = await analyseNature(user_input, prev_response, natures)
    if reaction.strip() != "":
        await message.add_reaction(reaction)

    async with message.channel.typing():

        async for chunk in agent_executer.astream(
            {"messages": val,
             "Affection": str(natures["Affection"]),
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Curious": str(natures["Curious"]),
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
                            print(response_text)
                        else:
                            response_text += msg.content
                            print(response_text)

        if response_text.strip():
            await message.author.send(response_text)
            final_text += response_text
            prev_response['text'] = response_text

    #  if final_text.strip() and not tool_called:
        #   chunkted = split_text(final_text)
        #   vector_store.add_documents(
        #       [memory_constructor(chunk) for chunk in chunkted])


async def main():
    bot_task = asyncio.create_task(client.start(TOKEN))
    api_task = asyncio.create_task(run_server())

    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
