from django.core.cache import cache

from .models import TwitchUser, Match, Game

QUEUE_TIMEOUT = 60 * 60 * 24

class Queue:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.channel = TwitchUser.from_username(channel_name)
        self.matches = []
        self._open = False

    @property
    def current_match(self):
        return self.matches[0] if self.matches else None

    def add_match(self, player1, player2):
        match = Match(player1=player1, player2=player2, channel=self.channel)
        match.save()

        self.matches.append(match)
        self.save()

    def remove_match(self, index):
        match = self.matches.pop(index)
        match.delete()
        self.save()

    def end_match(self):
        match = self.matches.pop(0)
        match.end()
        self.save()

    def clear(self):
        for match in self.matches:
            match.delete()
        self.matches = []
        self.save()

    def save(self):
        cache.set(f"queues.{self.channel_name}", self, timeout=QUEUE_TIMEOUT)

    def open(self):
        self._open = True
        self.save()

    def close(self):
        self._open = False
        self.save()

    def declare_winner(self, winner, losing_score):
        self.current_match.add_game(winner, losing_score)
        self.save()

    def is_empty(self):
        return len(self.matches) == 0

    def is_open(self):
        return self._open

    @staticmethod
    def get(channel_name):
        return cache.get(f"queues.{channel_name}")
