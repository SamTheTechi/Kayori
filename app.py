import os
import asyncio
from dotenv import load_dotenv

# LangGraph & LangChain
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults

from server import run_server
from services.vector_db import initalise_vector_db
from services.state_store import init_states
from core.discord_bot import setup_discord_bot

# tools and utils
from tools.reminder import ReminderTool
# from tools.calender.calender import CalenderAgentTool
from tools.spotify import SpotifyTool
from tools.user import UserTool
from tools.weather import WeatherTool
from util.llm_provider import llm_initializer
from util.custom_memory_saver import CustomMemorySaver
from util.agent_state import KayoriState
from templates.core.private_template import private_template
from templates.core.public_template import public_template


# --- Load Environment ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# --- Memory & Vector DB ---
memory = CustomMemorySaver()
vector_store = initalise_vector_db(api_key="PINECONE")

# --- Tools ---
private_tools = [
    TavilySearchResults(max_results=3),
    SpotifyTool(),
    UserTool(),
    WeatherTool,
    ReminderTool(userId=os.getenv("USER_ID"))
    # CalenderAgentTool(),
]

# just hardcoding rn coz it's a pain to setup rn, and im tired as shit
public_tools = [
    TavilySearchResults(max_results=3),
    WeatherTool,
    ReminderTool(userId="1387877964506464256")
]


# --- LLM Setup ---
llm = llm_initializer(model="gemini-2.5-flash", temperature=0.7)

# --- Agents ---
private_executer = create_react_agent(
    llm,
    private_tools,
    checkpointer=memory,
    prompt=private_template,
    state_schema=KayoriState,
)

public_executer = create_react_agent(
    llm,
    public_tools,
    checkpointer=memory,
    prompt=public_template,
    state_schema=KayoriState,
)

# --- Discord Bot Setup ---
client = setup_discord_bot(private_executer, public_executer, vector_store)


# --- Entry Point ---
async def main():
    await asyncio.gather(
        init_states(),
        client.start(TOKEN),
        run_server()
    )


if __name__ == "__main__":
    asyncio.run(main())
