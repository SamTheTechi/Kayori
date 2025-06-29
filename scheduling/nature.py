import os
import random
import discord
from dotenv import load_dotenv
from services.state_store import get_mood, set_mood

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("discord bot token not found")


intents = discord.Intents.default()
client = discord.Client(intents=intents)


# Changes the kayori's profile picture randomly.
async def change_pfp(client):
    try:
        files = [f for f in os.listdir("./pfp")]
        img_name = random.choice(files)
        img_path = os.path.join("./pfp", img_name)
        with open(img_path, "rb") as image:
            pfp = image.read()
            await client.user.edit(avatar=pfp)
            print("pfp updated")
    except Exception as e:
        print(f"error: {e}")


# Gradually stabilizes mood values towards a baseline of 0.
async def mood_drift():
    # stabilize mood over time toward 0 baseline
    raw = await get_mood()
    natures = {k: float(v) for k, v in raw.items()}

    for tone, strength in natures.items():
        if strength > 0:
            natures[tone] = round(strength - 0.01, 2)
        elif strength < 0:
            natures[tone] = round(strength + 0.01, 2)

        natures[tone] = max(-1.0, min(1.0, natures[tone]))

    print("mood", natures)
    await set_mood(**natures)


# Applies a sudden, random fluctuation to one of the mood tones.
async def mood_spike():
    # apply sudden mood fluctuation to a random tone
    raw = await get_mood()
    natures = {k: float(v) for k, v in raw.items()}

    tone = random.choice(list(natures.keys()))
    change = round(random.uniform(0.5, 0.7), 2) * random.choice([-1, 1])
    natures[tone] = round(natures[tone] + change, 2)

    natures[tone] = max(-1.0, min(1.0, natures[tone]))

    print("spike", natures)
    await set_mood(**natures)
