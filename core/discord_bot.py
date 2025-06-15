import os
import discord


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Kaori is online as {client.user}")


@client.event
async def on_message(message):
    pass


def start_discord_bot(token):
    client.run(token)
