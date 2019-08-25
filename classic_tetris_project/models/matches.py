from django.db import models
from django.utils import timezone

from .users import User, TwitchUser


class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    player2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    wins1 = models.IntegerField(default=0)
    wins2 = models.IntegerField(default=0)
    channel = models.ForeignKey(TwitchUser, null=True, on_delete=models.PROTECT)

    # Null until the match has ended
    ended_at = models.DateTimeField(null=True)

    def add_game(self, winner, losing_score):
        if winner == self.player1 or winner == self.player2:
            game = Game(match=self, winner=winner, losing_score=losing_score)
            game.save()

            if winner == self.player1:
                self.wins1 += 1
            else:
                self.wins2 += 1
            self.save()

        else:
            raise ValueError("Winner is not a player in the match")

    def get_current_winner(self):
        if self.wins1 > self.wins2:
            return self.player1
        elif self.wins2 > self.wins1:
            return self.player2
        else:
            return None

    def end(self):
        self.ended_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.player1} vs. {self.player2}"


class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.ForeignKey(User, on_delete=models.PROTECT)
    losing_score = models.IntegerField(null=True)

    ended_at = models.DateTimeField(auto_now_add=True)
