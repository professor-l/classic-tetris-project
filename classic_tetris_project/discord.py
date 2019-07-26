import discord
from .env import env

client = discord.Client()
guild_id = int(env("DISCORD_GUILD_ID"))
