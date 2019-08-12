from django.core.cache import cache

from .models import Match, Game

QUEUE_TIMEOUT = 60 * 60 * 24

class Queue:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.channel = TwitchUser.from_username(channel_name)
        self.matches = []
        self._open = False

    def add_match(self, player1, player2):
        match = Match(player1=player1, player2=player2, channel=self.channel)

        self.matches.append(Match(twitch_user1, twitch_user2))
        self.save()

    def remove_match(self, index):
        match = self.matches.pop(index)
        match.delete()
        self.save()

    def save(self):
        cache.set(f"queues.{self.channel_name}", self, timeout=QUEUE_TIMEOUT)

    def open(self):
        self._open = True
        self.save()

    def close(self):
        self._open = False
        self.save()

    def is_empty(self):
        return len(self.matches) == 0

    def is_open(self):
        return self._open

    @staticmethod
    def get(channel):
        return cache.get(f"queues.{channel_name}")
