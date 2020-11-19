import discord
import logging
import requests

from asgiref.sync import async_to_sync
from .env import env

DISCORD_API = "https://discord.com/api/"

client = discord.Client()
guild_id = int(env("DISCORD_GUILD_ID", default=0))
moderator_role_id = int(env("DISCORD_MODERATOR_ROLE_ID", default=0))
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


def get_guild():
    return client.get_guild(guild_id)

def get_guild_member(custom_guild_id, id):
    g = custom_guild_id or guild_id
    return async_to_sync(client.get_guild(g).fetch_member)(id)

def get_channel(id):
    return client.get_channel(id)

def get_emote(name):
    r = discord.utils.get(get_guild().emojis, name=name)
    return str(r) if r else None
def get_emoji(name):
    return get_emote(name)
