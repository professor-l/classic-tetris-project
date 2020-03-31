from django.db import models
from django.db.utils import OperationalError

from .twitch import TwitchChannel
from .users import TwitchUser


class CustomCommand(models.Model):
    
    twitch_channel = models.ForeignKey(TwitchChannel, on_delete=models.CASCADE)

    name = models.CharField(max_length=20)
    output = models.CharField(max_length=400, null=True, blank=True)
    alias_for = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)

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

    @staticmethod
    def get_command(channel, command_name):
        try:
            command = CustomCommand.objects.filter(twitch_channel=channel).get(name=command_name)
        except (CustomCommand.DoesNotExist, OperationalError):
            return False
        

        return command

    def wrap(self, context):
        from ..commands.command import CustomTwitchCommand
        return CustomTwitchCommand(context, self)
