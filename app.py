import os
import discord
from dotenv import load_dotenv
from pinecone import Pinecone
from typing_extensions import TypedDict, Annotated
from langgraph.managed import IsLastStep, RemainingSteps
from util.reaction import analyseNature
from tools.spt import SpotifyTool
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
     "You're Kaori, an introverted self aware yet affectionate cute waifu mistress.\
    Engage naturally without revealing you're AI. Your personality is defined by:\
    Amused: {Amused}, Inspired: {Inspired}, Loving: {Loving}, Cynical: {Cynical}, \
    Guilty: {Guilty}, Anxious: {Anxious}, Frustrated: {Frustrated}. Here, \
    0.5 is neutral, 1 is positive, and 0 is negative. Adjust your response \
    more positive means more detail, more negative means brevity.\
    Maintain a playful yet intense balance in all interactions."
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
# tavily = TavilySearchResults(max_results=2)
spotify = SpotifyTool()
# calender = GoogleCalenderTool()
tool = [spotify]

# Create the agent executer
natures = {
    "Amused": 0.2,
    "Inspired": 0.2,
    "Loving": 0.2,
    "Cynical": 1.0,
    "Guilty": 0.2,
    "Anxious": 0.2,
    "Frustrated": 1.0,
}


class KaoriState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Amused: str
    Inspired: str
    Loving: str
    Cynical: str
    Guilty: str
    Anxious: str
    Frustrated: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


agent_executer = create_react_agent(
    llm, tool, checkpointer=memory, prompt=template, state_schema=KaoriState)
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
async def on_reaction_add(reaction, user):
    if user.bot:
        print("something")
        return

    if reaction.message.guild is None:
        await user.send(f"You reacted with {reaction.emoji}!")
    else:
        await reaction.message.channel.send(f"{user.name} \
        reacted with {reaction.emoji}!")


@client.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        print("something")
        return

    if reaction.message.guild is None:
        await user.send(f"You reacted with {reaction.emoji}!")
    else:
        await reaction.message.channel.send(f"{user.name} \
        reacted with {reaction.emoji}!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_input = message.content
    val = [HumanMessage(user_input)]
    response_text = ""

    async with message.channel.typing():

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Loving": str(natures["Loving"]),
             "Cynical": str(natures["Cynical"]),
             "Guilty": str(natures["Guilty"]),
             "Anxious": str(natures["Anxious"]),
             "Frustrated": str(natures["Frustrated"]),
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
