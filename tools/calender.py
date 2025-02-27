import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, Annotated
from langgraph.managed import IsLastStep, RemainingSteps
from serchevents import CalendarSearchEvents
from createvent import CalendarCreateEvent
from langgraph.prebuilt import create_react_agent
from datetime import datetime, timezone
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("API_KEY"),
    temperature=0.1,
)

template = ChatPromptTemplate.from_messages([
    ("system",
        "You are an google calender manager you job is to\
        handle my google calender. this is the current time\
        {current_data_time} Respond concisely with only the necessary\
        scheduling details. Do not add extra commentary or text."
     ),
    ("placeholder", "{messages}"),
])

tool = [CalendarSearchEvents(), CalendarCreateEvent()]


class CalenderState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_data_time: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


agent_executer = create_react_agent(
    llm,
    tool,
    prompt=template,
    state_schema=CalenderState
)

config = {"configurable": {"thread_id": "abc123"}}


while True:
    val = input("sam: ")
    test = ""
    for chunk, metadata in agent_executer.stream(
        {
            "messages": val,
            "current_data_time": str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
        },
        config,
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage):
            chunk.pretty_print()
            test += chunk.content
    print(test)
