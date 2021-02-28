from django.db import models

from .users import User
from .events import Event
from .qualifiers import Qualifier


class Tournament(models.Model):
    name = models.CharField(max_length=64)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class TournamentPlayer(models.Model):
    qualifier = models.OneToOneField(Qualifier, on_delete=models.CASCADE,
                                     related_name="tournament_player")
    user = models.ForeignKey(User, related_name="tournament_players",
                             on_delete=models.PROTECT)
    event = models.ForeignKey(Tournament, related_name="tournament_players",
                              on_delete=models.CASCADE)
    seed = models.IntegerField()
