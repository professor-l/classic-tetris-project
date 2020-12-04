from django.db import models

from .users import TwitchUser
from ..util import memoize
from .. import twitch


class TwitchChannel(models.Model):
    twitch_user = models.OneToOneField(TwitchUser, on_delete=models.CASCADE, related_name="channel",
                                       primary_key=True)
    connected = models.BooleanField(default=False, db_index=True)

    @property
    def name(self):
        return self.twitch_user.username

    def summon_bot(self):
        self.connected = True
        self.save()
        twitch.client.join_channel(self.name)

    def eject_bot(self):
        self.connected = False
        self.save()
        twitch.client.leave_channel(self.name)

    @property
    @memoize
    def client_channel(self):
        return twitch.client.get_channel(self.name)

    def send_message(self, message):
        self.client_channel.send_message(message)

    def __str__(self):
        return str(self.twitch_user)
