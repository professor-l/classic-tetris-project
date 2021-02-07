# Uses disco instead of discordpy. This file is temporary; we'll probably end up switching
# everything over to disco eventually.

from disco.api.client import APIClient

from .env import env


DISCORD_USER_ID_WHITELIST = env("DISCORD_USER_ID_WHITELIST")

def create_client():
    return APIClient(env("DISCORD_TOKEN", default=""))


def send_direct_message(discord_user_id, *args, **kwargs):
    if env("DEBUG") and discord_user_id not in DISCORD_USER_ID_WHITELIST:
        print(f"Tried to send message to Discord user {discord_user_id}:")
        print(f"{args}, {kwargs}")
        return
    client = create_client()
    channel = client.users_me_dms_create(discord_user_id)
    client.channels_messages_create(channel, *args, **kwargs)

def send_channel_message(channel_id, *args, **kwargs):
    if env("DEBUG") and not env("DISCORD_CHANNEL_MESSAGES"):
        print(f"Tried to send message to Discord channel {channel_id}:")
        print(f"{args}, {kwargs}")
        return
    client = create_client()
    client.channels_messages_create(channel_id, *args, **kwargs)
