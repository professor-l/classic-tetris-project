from .command import Command, register_command
from ..util import Platform

@register_command("testmsg")
class TestMessageCommand(Command):
    usage = "testmsg"

    def execute(self, *username):
        username = " ".join(username)

        if self.context.platform == Platform.TWITCH:
            discord_user = Command.discord_user_from_username(username)
            discord_user.send_message("Test!")
        
        else:
            twitch_user = Command.twitch_user_from_username(username)
            twitch_user.send_message("Test!")
            