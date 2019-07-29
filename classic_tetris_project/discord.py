import discord
from .env import env

client = discord.Client()
guild_id = int(env("DISCORD_GUILD_ID"))
moderator_role_id = int(env("DISCORD_MODERATOR_ROLE_ID"))

def get_guild():
    return client.get_guild(guild_id)
