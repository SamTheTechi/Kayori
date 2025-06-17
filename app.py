import os
import asyncio

from server import run_server
from dotenv import load_dotenv
from services.vector_db import initalise_vector_db
from core.discord_bot import setup_discord_bot
from core.agent_executer import create_agent_executer
from tools.spt import SpotifyTool
from tools.calender import CalenderAgentTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold
load_dotenv()
os.getenv("TAVILY_API_KEY")

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
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

vector_store = initalise_vector_db(api_key="PINECONE")

# Tools available for Kaori
tavily = TavilySearchResults(max_results=2)
spotify = SpotifyTool()
calender = CalenderAgentTool()
tool = [spotify, tavily, calender]

agent_executer = create_agent_executer(llm, tool)

config = {"configurable": {"thread_id": "sameer"}}

client = setup_discord_bot(agent_executer, vector_store, config)


async def main():
    bot_task = asyncio.create_task(client.start(TOKEN))
    api_task = asyncio.create_task(run_server())

    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
