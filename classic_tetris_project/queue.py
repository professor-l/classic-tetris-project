from django.core.cache import cache

QUEUE_TIMEOUT = 60 * 60 * 24

class Queue:
    def __init__(self, channel):
        self.channel = channel
        self.matches = []
        self.open = True

    def add_match(self, match):
        self.matches.append(match)

    def save(self):
        cache.set(f"queues.{self.channel}", self, timeout=QUEUE_TIMEOUT)

    def close():
        self.open = False

    @staticmethod
    def get(channel):
        return cache.get(f"queues.{channel}")


    


class Match:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.games = []
        self.winner = None
    
class Game:



        
class Game:


vandweller roncli

!winner roncli 341,533
