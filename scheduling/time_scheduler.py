import os
import random
import discord
from langchain_core.messages import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from dotenv import load_dotenv
from util.balance_mood import balance_mood
from util.store import (
    update_context,
    natures,
    update_pfp
)

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()

client = discord.Client(intents=intents)


async def change_pfp(client):
    try:
        files = [f for f in os.listdir("./pfp")]
        img_name = random.choice(files)
        img_path = os.path.join("./pfp", img_name)
        update_pfp(img_path)
        with open(img_path, "rb") as image:
            pfp = image.read()
            await client.user.edit(avatar=pfp)
            print("pfp updated")
    except Exception as e:
        print(f"error: {e}")


async def good_morning(
        client,
        agent_executer,
        config,
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [
            SystemMessage(
                "Start the day with a warm and cheerful 'Good morning!' Wish the user a great day ahead in a friendly and uplifting way. "
                "Keep it short, positive, and under 50 words."
            ),
            HumanMessage("good morning!")
        ]

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
        update_context(response_text)
        await client.change_presence(status=discord.Status.online)

    except Exception as e:
        print(f"allpu {e}")


async def mood_drift():
    # stablise mood over time
    for tone, strength in natures.items():
        if (strength > 0.5):
            natures[tone] = round(strength - 0.01, 2)
        elif (strength < 0.5):
            natures[tone] = round(strength + 0.01, 2)


async def mood_spike():
    # give suddne mood spikes at certain interval
    random_mood = random.choice(list(natures.keys()))
    natures[random_mood] = round(random.uniform(0.75, 0.85), 2)


async def good_evening(
        client,
        agent_executer,
        config,
):
    try:
        user = await client.fetch_user(int(os.getenv("USER_ID")))
        response_text = ""
        val = [
            SystemMessage(
                "Greet the user with a heartfelt 'Good evening!' and then ask them how their day went in a warm and caring way. "
                "Ensure your response feels personal, friendly, and under 60 words. Avoid generic or robotic phrasing."
            ),
            HumanMessage("good evening!")
        ]
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
        update_context(response_text)
        await client.change_presence(status=discord.Status.idle)

    except Exception as e:
        print(e)
