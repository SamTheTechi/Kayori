import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Type
from pydantic import BaseModel, Field
from tools.deletevent import CalendarDeleteEvent
from tools.createvent import CalendarCreateEvent
from tools.searchevent import CalendarSearchEvent
from typing_extensions import TypedDict, Annotated
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import BaseTool
from langgraph.managed import IsLastStep, RemainingSteps
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
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

tool = [CalendarSearchEvent(), CalendarCreateEvent(),
        CalendarDeleteEvent()]


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


class CalenderAgentSchema(BaseModel):
    query: str = Field(...,
                       description="User request realted to google calender")


class CalenderAgentTool(BaseTool):
    name: str = "calender_agent_tool"
    description: str = "A specialized tool for managing calendar-related tasks\
    ,including checking schedule, planning and handling events.\
    Use it to answer questions about your plans, upcoming tasks, and\
    availability, as well as creating, deleting, and searching for events."
    args_schema: Type[CalenderAgentSchema] = CalenderAgentSchema

    def _run(self, query: str) -> str:
        response_text = ""
        for chunk, metadata in agent_executer.stream(
            {
                "messages": query,
                "current_data_time": str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
            },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        return str(response_text)

    def __call__(self, query: str) -> str:
        return self._run(query)
