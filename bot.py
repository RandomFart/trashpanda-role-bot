import os
import discord
from dotenv import load_dotenv

import config


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    guild = client.get_guild(config.GUILD_ID)

    if guild is None:
        print("Could not find guild. Check GUILD_ID and make sure the bot is in the server.")
        await client.close()
        return
    
    print(f"Connected to server: {guild.name}")
    print()
    print("Roles found:")

    for role in guild.roles:
        print(f"{role.name}: {role.id}")

    await client.close()


client.run(TOKEN)