from django.db import models

from .twitch import TwitchChannel
from .users import TwitchUser


class CustomCommand(models.Model):
    
    twitch_channel = models.ForeignKey(TwitchChannel, on_delete=models.CASCADE)

    name = models.CharField(max_length=20)
    output = models.CharField(max_length=400, null=True)
    alias_for = models.ForeignKey("self", null=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(
                fields=["twitch_channel"]
            )
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["twitch_channel", "name"],
                name="unique channel plus command"
            )
        ]
