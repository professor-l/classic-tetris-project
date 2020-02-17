from django.core.cache import cache

from .models import TwitchUser, Match, Game

QUEUE_TIMEOUT = 60 * 60 * 24

class Queue:
    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.channel = TwitchUser.from_username(channel_name)
        self._matches = []
        self._open = False

    @property
    def current_match(self):
        return self._matches[0] if self._matches else None

    def get_match(self, index):
        return self._matches[index - 1]

    def add_match(self, player1, player2):
        match = Match(player1=player1, player2=player2, channel=self.channel)
        match.save()

        self._matches.append(match)
        self.save()

    def insert_match(self, player1, player2, index):

        try:
            index = int(index)
        except:
            raise CommandException("Invalid index.")


        if len(self._matches) < index:
            self.add_match(player1, player2)
            return

        match = Match(player1=player1, player2=player2, channel=self.channel)
        match.save()

        self._matches.insert(index - 1, match)
        self.save()

    def remove_match(self, index):
        match = self._matches.pop(index - 1)
        match.delete()
        self.save()

    def end_match(self):
        match = self._matches.pop(0)
        match.end()
        self.save()

    def clear(self):
        for match in self._matches:
            match.delete()
        self._matches = []
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
        return len(self._matches) == 0

    def is_open(self):
        return self._open

    @staticmethod
    def get(channel_name):
        return cache.get(f"queues.{channel_name}")

    def __len__(self):
        return len(self._matches)

    def __iter__(self):
        return iter(self._matches)

    def __bool__(self):
        return True
