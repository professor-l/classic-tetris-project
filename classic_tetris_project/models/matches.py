from django.db import models

from .users import User, TwitchUser


class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.PROTECT)
    player2 = models.ForeignKey(User, on_delete=models.PROTECT)
    wins1 = models.IntegerField(default=0)
    wins2 = models.IntegerField(default=0)
    channel = models.ForeignKey(TwitchUser, null=True)

    # Null until the match has ended
    ended_at = models.DateTimeField(null=True)

    def add_game(self, winner, losing_score):
        game = Game(match=self, winner=winner, losing_score=losing_score)
        game.save()

class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.ForeignKey(User, on_delete=models.PROTECT)
    losing_score = models.IntegerField()

    ended_at = models.DateTimeField(auto_now_add=True)

