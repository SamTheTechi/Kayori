import os
import asyncio
import random
import discord
from util.get_current_time import get_current_time
from services.state_store import get_mood
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


async def random_status(client, agent_executer, config):
    try:
        response_text = ""
        val = [
            SystemMessage(
                "Respond with a very short Discord status (3–5 words) that reflects a thoughtful or meaningful mood. "
                "Avoid personal or private information. Keep it funny, sarcastic, and suitable for a public profile. "
                "Only return the status — no explanations or extra text."
            ),
            HumanMessage("What's on your mind?")
        ]

        mood = await get_mood()

        async for chunk, metadata in agent_executer.astream(
            {
                "messages": val,
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

        await client.change_presence(activity=discord.Game(f"{response_text}"))

        async def reset_presence():
            await asyncio.sleep(60)
            await client.change_presence(activity=None)

        asyncio.create_task(reset_presence())

    except Exception as e:
        print(f"Error while setting morning greeting status: {e}")


# Changes the kayori's profile picture randomly.
async def change_pfp(client):
    try:
        files = [f for f in os.listdir("./pfp")]
        img_name = random.choice(files)
        img_path = os.path.join("./pfp", img_name)
        with open(img_path, "rb") as image:
            pfp = image.read()
            await client.user.edit(avatar=pfp)
    except Exception as e:
        print(f"error: {e}")
