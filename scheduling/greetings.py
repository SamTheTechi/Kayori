import os
import discord
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from util.get_current_time import get_current_time
from util.balance_mood import balance_mood
from services.state_store import get_mood


# Sends a good morning message to the user.
async def good_morning(client, agent_executer, config):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [
            SystemMessage(
                "Start the day with a warm and cheerful 'Good morning!' Wish \
                the user a great day ahead in a friendly and uplifting way. \
                Keep it short, positive, and under 50 words."
            ),
            HumanMessage("good morning!")
        ]
        mood = await get_mood()

        await balance_mood()

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(mood["Affection"]),
             "Amused": str(mood["Amused"]),
             "Inspired": str(mood["Inspired"]),
             "Frustrated": str(mood["Frustrated"]),
             "Concerned": str(mood["Concerned"]),
             "Curious": str(mood["Curious"]),
             "current_time": str(get_current_time())
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        print("morning wished")
        await user.send(response_text)

        await client.change_presence(status=discord.Status.online)

    except Exception as e:
        print(f"error while evening greeting {e}")


# Sends a good evening message to the user.
async def good_evening(client, agent_executer, config):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [
            SystemMessage(
                "Greet the user with a heartfelt 'Good evening!' and then ask\
                them how their day went in a warm and caring way. Ensure \
                your response feels personal, friendly, and under 60 words.\
                Avoid generic or robotic phrasing."
            ),
            HumanMessage("good evening!")
        ]
        mood = await get_mood()

        await balance_mood()

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(mood["Affection"]),
             "Amused": str(mood["Amused"]),
             "Inspired": str(mood["Inspired"]),
             "Frustrated": str(mood["Frustrated"]),
             "Concerned": str(mood["Concerned"]),
             "Curious": str(mood["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        print("evening wished")

        await user.send(response_text)

        await client.change_presence(status=discord.Status.idle)

    except Exception as e:
        print(f"error while morning greeting {e}")
