from django.db import models
from django.utils import timezone

from .users import User


class Side(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="+")
    timestamp = models.DateTimeField()

    @staticmethod
    def log(user):
        Side.objects.create(user=user, timestamp=timezone.now())

