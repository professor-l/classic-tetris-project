import discord
import logging
from .env import env

client = discord.Client()
guild_id = int(env("DISCORD_GUILD_ID"))
moderator_role_id = int(env("DISCORD_MODERATOR_ROLE_ID"))
logger = logging.getLogger("discord-bot")

def get_guild():
    return client.get_guild(guild_id)

def get_channel(id):
    return client.get_channel(id)