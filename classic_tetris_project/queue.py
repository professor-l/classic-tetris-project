from django.core.cache import cache

QUEUE_TIMEOUT = 60 * 60 * 24

class Queue:
    def __init__(self, channel):
        self.channel = channel
        self.matches = []
        self._open = False

    def add_match(self, twitch_user1, twitch_user2):
        self.matches.append(Match(twitch_user1, twitch_user2))
        self.save()

    def save(self):
        cache.set(f"queues.{self.channel}", self, timeout=QUEUE_TIMEOUT)

    def open(self):
        self._open = True
        self.save()

    def close(self):
        self._open = False
        self.save()



    @property
    def is_open(self):
        return self._open

    @staticmethod
    def get(channel):
        return cache.get(f"queues.{channel}")


class Match:
    def __init__(self, twitch_user1, twitch_user2):
        self.twitch_user1 = twitch_user1
        self.twitch_user2 = twitch_user2
        self.games = []
        self.winner = None
    
class Game:
    def declare_winner(winner):
        self.winner = winner

