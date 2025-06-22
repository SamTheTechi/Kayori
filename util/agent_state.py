from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep, RemainingSteps


class KayoriState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Affection: str
    Amused: str
    Inspired: str
    Frustrated: str
    Concerned: str
    Curious: str
    current_time: str
    replying_to: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
