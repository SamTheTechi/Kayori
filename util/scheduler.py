import os
import random
import discord
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from typing import Dict
from dotenv import load_dotenv
from util.balance_mood import balance_mood
load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()

client = discord.Client(intents=intents)


async def change_pfp(client):
    try:
        files = [f for f in os.listdir("./pfp")]
        img_path = os.path.join("./pfp", random.choice(files))
        with open(img_path, "rb") as image:
            pfp = image.read()
            await client.user.edit(avatar=pfp)
            print("pfp updated")
    except Exception as e:
        print(f"error: {e}")


async def good_morning(
        client,
        agent_executer,
        config, natures: Dict[str, float],
        prev_response: Dict[str, str]
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [SystemMessage("wish a simple good morning and have a grate \
        day ahead, under 50 words"),
               HumanMessage("gm")]
        balance_mood(natures)

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(natures["Affection"]),
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Curious": str(natures["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        print("morning wished")
        await user.send(response_text)
        prev_response['text'] = response_text
        await client.change_presence(status=discord.Status.online)

    except Exception as e:
        print(f"allpu {e}")


async def good_evening(
        client,
        agent_executer,
        config, natures: Dict[str, float],
        prev_response: Dict[str, str]
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [SystemMessage("wish a simple good evening and ask how\
            you day goes!, under 60 words"),
               HumanMessage("good evening!")]
        balance_mood(natures)

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(natures["Affection"]),
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Curious": str(natures["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content

        print("evening wished")
        await user.send(response_text)
        prev_response['text'] = response_text
        await client.change_presence(status=discord.Status.idle)

    except Exception as e:
        print(e)


async def random_convo(
        client,
        agent_executer,
        config, natures: Dict[str, float],
        prev_response: Dict[str, str]
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [SystemMessage("start a conversation!"),
               HumanMessage("ge"),
               AIMessage("")]
        balance_mood(natures)

        async for chunk, metadata in agent_executer.astream(
            {"messages": val,
             "Affection": str(natures["Affection"]),
             "Amused": str(natures["Amused"]),
             "Inspired": str(natures["Inspired"]),
             "Frustrated": str(natures["Frustrated"]),
             "Anxious": str(natures["Anxious"]),
             "Curious": str(natures["Curious"]),
             },
            config,
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage):
                response_text += chunk.content
                chunk.pretty_print()

        print("evening wished")
        await user.send(response_text)
        prev_response['text'] = response_text
        await client.change_presence(status=discord.Status.idle)

    except Exception as e:
        print(e)
