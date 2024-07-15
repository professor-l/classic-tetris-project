from .command import Command
from ..util import Platform, DocSection

@Command.register()
class TestCommand(Command):
    """
    Send a test message.
    """
    aliases = ("test", "devtest")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "test"
    section = DocSection.OTHER

    def execute(self):
        self.send_message("Test!")
