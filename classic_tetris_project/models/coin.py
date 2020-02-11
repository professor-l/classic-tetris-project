from django.db import models
from django.utils import timezone

from .users import User

class Coin(models.Model):

    heads = models.IntegerField(default=0)
    tails = models.IntegerField(default=0)
    sides = models.IntegerField(default=0)

    @staticmethod
    def add_flip(s, user):
        if s == "Heads!":
            coin.heads += 1
        elif s == "Tails!":
            coin.tails += 1
        else:
            coin.sides += 1
            Side(user)
        coin.save()

class Side(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    timestamp = models.DateTimeField()
    def __init__(self, user):
        self.user = user
        self.timestamp = timezone.now()
        self.save()

coin = Coin.objects.all()[0]
