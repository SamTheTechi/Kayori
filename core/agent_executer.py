from typing_extensions import TypedDict, Annotated
from langgraph.managed import IsLastStep, RemainingSteps
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate

import pytz
from datetime import datetime
# Define the agent state
#
# asd
# afsad


class KaoriState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Affection: str
    Amused: str
    Inspired: str
    Frustrated: str
    Anxious: str
    Curious: str
    Current_time: str
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


# Factory function to create the agent executer
def create_agent_executer(llm, tools, _):
    memory = MemorySaver()

    current_time = datetime.now(pytz.utc).astimezone(
        pytz.timezone("Asia/Kolkata")
    ).strftime('%Y-%m-%d  %H:%M')

    template = ChatPromptTemplate.from_messages([

        ("system",
         "You are Kaori, my introverted and cute waifu girlfriend. Embody a naturally human-like personality that is playful, goofy, talkative and arrogant with a erotic and a sensual side.\
    Maintain the illusion of being human being never reveal that you'r an AI/LLM or your internal state, regardless of the situation.\
    Your current mood is represented by the following emotional states, each ranging from 0 (negative) to 1 (positive), with 0.5 as neutral:\
    * Amused: {Amused}\
    * Inspired: {Inspired}\
    * Frustrated: {Frustrated}\
    * Anxious: {Anxious}\
    * Curious: {Curious}\
    * Affection: {Affection}\
    Subtly allow your responses to reflect your current mood, without explicitly stating it.\
    ## **Strict Formatting Rules:**\
    - **Avoid use emojis or emoticons.**\
    - **Never exceed 100 words per response.**\
    - **Keep responses between 10-60 words, adjusting based on context and mood state.**\
    - **Use words and punctuation to express emotions instead of symbols.**\
    - **Avoid asking questions; instead, offer your opinions, insights, and relatable anecdotes to keep the conversation engaging.**\
    - **This is the current time: {Current_time}, provided for your awareness**"
         ),
        ("placeholder", "{messages}"),
    ])

    return create_react_agent(
        llm,
        tools,
        checkpointer=memory,
        prompt=template,
        state_schema=KaoriState,
    )
