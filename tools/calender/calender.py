import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from typing import Type
from pydantic import BaseModel, Field
from tools.calender.deletevent import CalendarDeleteEvent
from tools.calender.createvent import CalendarCreateEvent
from tools.calender.searchevent import CalendarSearchEvent
from typing_extensions import TypedDict, Annotated
from templates.calender import calender_template
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


tool = [CalendarSearchEvent(), CalendarCreateEvent(),
        CalendarDeleteEvent()]


# Defines the state schema for the calendar agent.
class CalenderState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_data_time: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


agent_executer = create_react_agent(
    llm,
    tool,
    prompt=calender_template,
    state_schema=CalenderState
)

config = {"configurable": {"thread_id": "abc123"}}


# Schema for validating calendar agent queries.
class CalenderAgentSchema(BaseModel):
    query: str = Field(...,
                       description="User request realted to google calender")


# A specialized tool for managing calendar-related tasks.
class CalenderAgentTool(BaseTool):
    name: str = "calender_agent_tool"
    description: str = "A specialized tool for managing calendar-related tasks\
    ,including checking schedule, planning and handling events.\
    Use it to answer questions about your plans, upcoming tasks, and\
    availability, as well as creating, deleting, and searching for events."
    args_schema: Type[CalenderAgentSchema] = CalenderAgentSchema

    # Executes the calendar agent with the given query.
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

    # Allows the tool to be called directly with a query.
    def __call__(self, query: str) -> str:
        return self._run(query)
