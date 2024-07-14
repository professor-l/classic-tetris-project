import logging
import requests
from typing import Union

import discord

from asgiref.sync import async_to_sync
from .env import env

DISCORD_API = "https://discord.com/api/"
GUILD_ID = int(env("DISCORD_GUILD_ID", default=0))
MAINTENANCE_CHAN_ID = int(env("DISCORD_MAINTENANCE_CHAN_ID", default=0))
MODERATOR_ROLE_ID = int(env("DISCORD_MODERATOR_ROLE_ID", default=0))

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)
client = discord.Client(intents=intents)
logger = logging.getLogger("discord-bot")

def wrap_user_dict(user_dict):
    return discord.user.BaseUser(state=None, data=user_dict)

class APIClient:
    def __init__(self, discord_token):
        self.discord_token = discord_token
        self.headers = {
            "Authorization": f"Bot {self.discord_token}",
        }

    # TODO Better respect Discord's rate limiting:
    # https://discord.com/developers/docs/topics/rate-limits
    def _request(self, endpoint, params={}):
        response = requests.get(f"{DISCORD_API}{endpoint}", params=params, headers=self.headers)
        return response.json()

    def user_from_id(self, user_id):
        return wrap_user_dict(self._request(f"users/{user_id}"))

API = APIClient(env("DISCORD_TOKEN", default=""))


def get_guild() -> Union[discord.Guild,None]:
    return client.get_guild(GUILD_ID)

# Returns the guild member of the Discord user for the given guild id.
# If not found, returns the guild member for the bot's guild.
# Otherwise, returns None.
def get_guild_member(user_id, guild_id=None):
    def _get_member(guild_id):
        guild = client.get_guild(guild_id)
        if guild:
            return guild.get_member(user_id)
    return _get_member(guild_id) or _get_member(GUILD_ID) or None

def get_channel(id):
    channel = client.get_channel(id)
    assert isinstance(channel, discord.abc.Messageable)
    return channel

def get_emote(name):
    guild = get_guild()
    assert guild is not None
    r = discord.utils.get(guild.emojis, name=name)
    return str(r) if r else None
def get_emoji(name):
    return get_emote(name)
