from .command import Command
from ..util import Platform, DocSection

@Command.register()
class LinkCommand(Command):
    """
    Prints instructions for linking accounts from multiple platforms.
    """
    aliases = ("link", "linkaccount")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "link"
    section = DocSection.ACCOUNT

    def execute(self):
        self.send_message("To link your Twitch or Discord account, head to our website and click 'Login' at the top right: https://go.ctm.gg.  Once there, you can view and edit your profile.")


# TODO: unlink command lmao
