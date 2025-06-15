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
    natures[random_mood] += round(random.uniform(
        0.25, 0.35), 2) * random.choice([-1, 1])
