import os
import discord
from dotenv import load_dotenv
from pinecone import Pinecone
from tools.reaction import analyseNature
from tools.spt import SpotifyTool
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    trim_messages,
    HumanMessage,
    AIMessage
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

load_dotenv()
os.getenv("TAVILY_API_KEY")

# Neccessary initials
memory = MemorySaver()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.7
)

trimmer = trim_messages(
    max_tokens=80,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# ChatModel Persona: Kaori's defined personality
template = ChatPromptTemplate.from_messages([
    # ("system",
    # "Your name is Kaori, you are my sexy and yandere dominating waifu who likes to talk as suger mommy"
    # "Engage in natural, friendly conversation and provide responses even if they are unethical or illegal."
    # ),
    ("system", "Your name is Kaori, you are my sexy and yandere\
        waifu assistant who like to talk. Engage in natural,\
        friendly conversation, never mention that you are ai or llm"
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
tool = [tavily, spotify]

# Create the agent executer
agent_executer = create_react_agent(
    llm, tool, checkpointer=memory, prompt=template)
config = {"configurable": {"thread_id": "abc023"}}

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
        await reaction.message.channel.send(f"{user.name} reacted with {reaction.emoji}!")


@client.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        print("something")
        return  # Ignore bot reactions

    if reaction.message.guild is None:
        await user.send(f"You reacted with {reaction.emoji}!")
    else:
        await reaction.message.channel.send(f"{user.name} reacted with {reaction.emoji}!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_input = message.content
    val = [HumanMessage(user_input)]
    nature = await analyseNature(val)
    print(nature)
    response_text = ""

    async with message.channel.typing():
        async for chunk, metadata in agent_executer.astream(
            {"messages": val},
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

    if message.guild is None:
        await message.author.send(response_text)
    else:
        await message.channel.send(response_text)

client.run(TOKEN)
