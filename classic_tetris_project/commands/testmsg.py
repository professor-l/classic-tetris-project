from .command import Command
from ..util import Platform

@Command.register("testmsg",
                  usage="testmsg")
class TestMessageCommand(Command):
    def execute(self, *username):
        username = " ".join(username)

        if self.context.platform == Platform.TWITCH:
            discord_user = Command.discord_user_from_username(username)
            discord_user.send_message("Test!")

        else:
            twitch_user = Command.twitch_user_from_username(username)
            twitch_user.send_message("Test!")
