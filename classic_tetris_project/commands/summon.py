from django.core.exceptions import ObjectDoesNotExist

from ..util import Platform
from .command import Command, CommandException
from .. import twitch


SUMMON_LINK = "https://discordapp.com/api/oauth2/authorize?client_id=544534930114347023&permissions=378944&redirect_uri=https%3A%2F%2Fmonthlytetris.info%2Foauth%2Fauthorize%2F&scope=bot"

@Command.register("summon",
                         usage="summon")
class SummonCommand(Command):
    def execute(self):
        if self.context.platform == Platform.TWITCH:

            channel = self.context.platform_user.get_or_create_channel()
            self.summon_bot(channel)

        elif self.context.platform == Platform.DISCORD:
            self.send_message(f"Invite the bot to your server: <{SUMMON_LINK}>") 
        
    def summon_bot(self, channel):

        if channel.connected:
            raise CommandException(f"I'm already in #{channel.name}!")

        channel.summon_bot()
        self.context.platform_user.send_message(f"Ok, I've joined #{channel.name}. Message me "
                                                "\"!pleaseleavemychannel\" at any time to "
                                                "make me leave.")
        channel.send_message(f"Hi, I'm {twitch.client.username}!")

@Command.register("pleaseleavemychannel",
                         usage="pleaseleavemychannel")
class LeaveCommand(Command):
    def execute(self):

        try:
            twitch_user = self.context.user.twitch_user
            channel = twitch_user.channel
        except ObjectDoesNotExist:
            channel = None

        if not (channel and channel.connected):
            raise CommandException(f"I'm not in #{twitch_user.username}!")

        channel.eject_bot()
        self.send_message("Bye!")
