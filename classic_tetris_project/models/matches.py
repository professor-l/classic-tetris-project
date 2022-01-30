from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .users import User
from .twitch import TwitchChannel


class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    player2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    wins1 = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    wins2 = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    channel = models.ForeignKey(TwitchChannel, null=True, on_delete=models.PROTECT)
    vod = models.URLField(null=True, blank=True)
    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name="+", db_index=False)

    start_date = models.DateTimeField(null=True, blank=True)
    # Null until the match has ended
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'matches'

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

    def winner_wins(self):
        return max([self.wins1, self.wins2])

    def loser_wins(self):
        return min([self.wins1, self.wins2])

    def end(self, reported_by):
        if not self.ended_at:
            self.ended_at = timezone.now()
        self.reported_by = reported_by
        self.save()
        if hasattr(self, "tournament_match"):
            self.tournament_match.update_from_match()

    def __str__(self):
        return f"{self.player1} vs. {self.player2}"


class Game(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    winner = models.ForeignKey(User, on_delete=models.PROTECT)
    losing_score = models.IntegerField(null=True)

    ended_at = models.DateTimeField(auto_now_add=True)
