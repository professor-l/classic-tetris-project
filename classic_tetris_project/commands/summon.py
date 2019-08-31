from django.core.exceptions import ObjectDoesNotExist

from .command import Command, CommandException
from .. import twitch

@Command.register_twitch("summon",
                         usage="summon")
class SummonCommand(Command):
    def execute(self):
        self.check_private()

        channel = self.context.platform_user.get_or_create_channel()
        if channel.connected:
            raise CommandException(f"I'm already in #{channel.name}!")

        channel.summon_bot()
        self.send_message(f"Ok, I've joined #{channel.name}. Message me \"!pleaseleavemychannel\" "
                          "at any time to make me leave.")
        channel.send_message(f"Hi, I'm {twitch.client.username}!")


@Command.register_twitch("pleaseleavemychannel",
                         usage="pleaseleavemychannel")
class LeaveCommand(Command):
    def execute(self):
        self.check_private()

        try:
            channel = self.context.platform_user.channel
        except ObjectDoesNotExist:
            channel = None

        if not (channel and channel.connected):
            raise CommandException(f"I'm not in #{self.context.platform_user.username}!")

        channel.eject_bot()
        self.send_message("Bye!")
