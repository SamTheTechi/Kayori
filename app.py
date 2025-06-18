import os
import asyncio
from dotenv import load_dotenv

# LangGraph & LangChain
from typing_extensions import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep, RemainingSteps
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults

# Local modules
# from server import run_server
from services.vector_db import initalise_vector_db
from core.discord_bot import setup_discord_bot
from core.llm_provider import llm_initializer
# from tools.filter_validate_tools import filter_valid_tools
from tools.calender.calender import CalenderAgentTool
from tools.spt import SpotifyTool
from templates.core.private_template import private_template
from templates.core.public_template import public_template


# --- Load Environment ---
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# --- Memory & Vector DB ---
memory = MemorySaver()
vector_store = initalise_vector_db(api_key="PINECONE")

# --- Tools ---
private_tools = [
    TavilySearchResults(max_results=3),
    SpotifyTool(),
    CalenderAgentTool(),
]
public_tools = [
    TavilySearchResults(max_results=3),
]


class KayoriState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Affection: str
    Amused: str
    Inspired: str
    Frustrated: str
    Concerned: str
    Curious: str
    current_time: str
    # procedural_memory: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


# --- LLM Setup ---
llm = llm_initializer(model="gemini-2.0-flash", temperature=0.7)

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
        client.start(TOKEN),
        # run_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
