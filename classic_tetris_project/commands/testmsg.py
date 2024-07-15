from .command import Command
from ..util import Platform, DocSection

# this is so abusable it should've been disabled years ago lmao
# @Command.register()
class TestMessageCommand(Command):
    """
    Send a test message to the specified user in a private channel.
    """
    aliases = ("testmsg",)
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "testmsg <user>"
    section = DocSection.OTHER

    def execute(self, *username):
        username = " ".join(username)

        platform_user = self.platform_user_from_username(username)
        platform_user.send_message("Test!")
