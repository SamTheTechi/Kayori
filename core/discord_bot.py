import os
import discord
import json
import asyncio
from services.redis_db import redis_client, MESSAGE_QUEUE, MESSAGE_SET
from dotenv import load_dotenv

# Internal core modules
from core.scheduler import setup_scheduler
from core.message_handler import message_handler

load_dotenv()
USER_ID = int(os.getenv("USER_ID"))


def setup_discord_bot(private_executer, public_executer, vector_store):

    # Set up Discord client with necessary intents
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        try:
            # Start any scheduled tasks
            setup_scheduler(client, private_executer, vector_store, USER_ID)

            # Start the async message processing handler (from Redis queue)
            asyncio.create_task(
                message_handler(
                    client,
                    private_executer,
                    public_executer,
                    vector_store,
                    USER_ID
                )
            )

            print(f"Kayori is online as {client.user}")
        except Exception as e:
            print(f"error: {e}")

    @client.event
    async def on_message(message):
        # Ignore bot's own messages
        if message.author == client.user:
            return

        try:
            # Prepare message payload to be processed asynchronously
            payload = {
                "message_id": message.id,
                "channel_id": message.channel.id,
                "author_id": message.author.id,
                "content": message.content,
                "is_dm": isinstance(message.channel, discord.DMChannel)
            }

            # Push the message payload into Redis queue for async handling
            await redis_client.lpush(MESSAGE_QUEUE, json.dumps(payload))

            # Push the author+channel to count the number of acitive user in server and reply accondely
            if not (isinstance(message.channel, discord.DMChannel)):
                await redis_client.sadd(MESSAGE_SET, f"{message.author.id}:{message.channel.id}")

        except Exception as e:
            print(f"redis not working here: {e}")

    return client
