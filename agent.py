import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

os.getenv("TAVILY_API_KEY")
memory = MemorySaver()
search = TavilySearchResults(max_results=2)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.8)

agent_executor = create_react_agent(llm, [search], checkpointer=memory)

config = {"configurable": {"thread_id": "abc123"}}

for chunk in agent_executor.stream(
    {"messages": [HumanMessage(content="hi im bob!")]}, config
):
    print(chunk)

for chunk in agent_executor.stream(
    {"messages": [HumanMessage(content="whats my name?")]}, config
):
    print(chunk)
