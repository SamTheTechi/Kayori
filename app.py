import os
import discord
from dotenv import load_dotenv
from pinecone import Pinecone
from typing_extensions import TypedDict, Annotated
from langgraph.managed import IsLastStep, RemainingSteps
from util.reaction import analyseNature
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
    BaseMessage
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
     {Frustrated}, Anxious: {Anxious}, Cynical: {Cynical}. Here\
     , 0.5 is neutral, 1 is positive, and 0 is negative. Adjust your\
     response—more positive means more detail, more negative means\
     brevity. Maintain a playful yet intense balance in all interactions.\
     Keep responses concise and do not exceed 150 words per conversation."
     ),
    ("placeholder", "{messages}"),
])

# Vector DataBase init
pc = Pinecone(api_key=os.getenv("PINECONE"))
pineconeIndex = pc.Index("kaori")

embedding = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv('EMBD'),
    model_name="sentence-transformers/all-mpnet-base-v2"
)

vector_store = PineconeVectorStore(embedding=embedding, index=pineconeIndex)

# Tools available for Kaori
tavily = TavilySearchResults(max_results=2)
spotify = SpotifyTool()
calender = CalenderAgentTool()
tool = [spotify, tavily, calender]

# Create the agent executer
natures = {
    "Amused": 0.4,
    "Inspired": 0.4,
    "Frustrated": 0.8,
    "Anxious": 0.4,
    "Cynical": 0.8,
}


class KaoriState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Amused: str
    Inspired: str
    Frustrated: str
    Anxious: str
    Cynical: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


agent_executer = create_react_agent(
    llm, tool, checkpointer=memory, prompt=template, state_schema=KaoriState, t)
config = {"configurable": {"thread_id": "abc123"}}

# Discord bot setup
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Kaori is online as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_input = message.content
    val = [HumanMessage(user_input)]
    response_text = ""

    await analyseNature(val, natures)
    async with message.channel.typing():

        print(natures)
        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Cynical": str(natures["Cynical"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content
                chunk.pretty_print()

    if message.guild is None:
        await message.author.send(response_text)
    else:
        await message.channel.send(response_text)

client.run(TOKEN)
