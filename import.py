import json
from tqdm import tqdm
from django.db.utils import OperationalError

from classic_tetris_project.models import *

def import_users(filename):
    print("Importing users")
    with open(filename) as f:
        users_data = json.load(f)

    for twitch_username, data in tqdm(users_data.items()):
        try:
            twitch_user = TwitchUser.from_username(twitch_username)
            if twitch_user:
                user = twitch_user.user
                user.ntsc_pb = data["pb"]
                user.save()
        except OperationalError:
            print(f"Failed to import data for {twitch_username}")

def import_channels(filename):
    print("Importing channels")
    with open(filename) as f:
        channels = [line.strip().replace(",", "") for line in f]

    for channel_name in tqdm(channels):
        try:
            twitch_user = TwitchUser.from_username(channel_name)
            if twitch_user:
                channel = twitch_user.get_or_create_channel()
                channel.connected = True
                channel.save()
        except OperationalError:
            print(f"Failed to import channel {channel_name}")

import_users("db/data.json")
import_channels("db/channels.txt")
