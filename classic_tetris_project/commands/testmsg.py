from .command import Command, register_command
from ..util import Platform

@register_command("testmsg")
class TestMessageCommand(Command):
    usage = "testmsg"

    def execute(self, username):
        # TODO: implement cross-platform
        discord_user = Command.discord_user_from_username(username)
        discord_user.send_message("Test!")
