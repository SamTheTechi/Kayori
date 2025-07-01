import time
import discord
import asyncio
from util.agent_state import ONLINE, IDLE
from services.redis_db import redis_client, BOT_PRESENCE, BOT_LAST_ACTIVITY


class PresenceHandler:
    def __init__(self, client):
        self.client = client

    async def start_monitor(self):
        while True:
            # Check every 60 seconds
            await asyncio.sleep(60)
            try:
                last_tm = await redis_client.get(BOT_LAST_ACTIVITY)

                if last_tm is None:
                    continue

                last_time = float(last_tm)
                current_time = time.time()

                # If inactive for more than 3 minutes, go idle
                if current_time - last_time > 60 * 3:
                    await self.client.change_presence(status=discord.Status.idle)
                    await redis_client.set(BOT_PRESENCE, IDLE)
            except Exception as e:
                print("Error checking idle status: ", e)

    async def update_presence(self):
        try:
            # If currently idle, switch back to online
            if await redis_client.get(BOT_PRESENCE) == IDLE:
                await self.client.change_presence(status=discord.Status.online)
                await redis_client.set(BOT_PRESENCE, ONLINE)

            # Refresh activity time
            await redis_client.set(BOT_LAST_ACTIVITY, str(time.time()))
        except Exception as e:
            print("Error updating presence:", e)
