from .command import Command
from ..util import Platform, DocSection

COMMANDS_URL = "https://github.com/professor-l/classic-tetris-project/blob/master/docs/COMMANDS.md"
SOURCECODE_URL = "https://github.com/professor-l/classic-tetris-project"

@Command.register()
class HelpCommand(Command):
    """
    Prints a link to the complete command reference.
    """
    aliases = ("help", "commands")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "help"
    section = DocSection.OTHER

    def execute(self):
        self.send_message(f"All available commands are documented at {COMMANDS_URL}")

@Command.register()
class SourceCodeCommand(Command):
    """
    Prints a link to the bot's source code.
    """
    aliases = ("source", "code", "sourcecode")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "source"
    section = DocSection.OTHER

    def execute(self):
        self.send_message(f"The source code for this bot can be found here: {SOURCECODE_URL}")

@Command.register()
class StencilCommand(Command):
    """
    Prints out info on, and link to download, the (in)famous Stencil.
    """
    aliases = ("stencil",)
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "stencil"
    section = DocSection.OTHER

    def execute(self):
        self.send_message("The stencil helps the streamer line up your Tetris playfield with their "
                          "broadcast scene. Link here: https://go.ctm.gg/stencil")

@Command.register()
class CTMDiscordCommand(Command):
    """
    Prints a link to the Classic Tetris Monthly discord server (i.e.
    https://go.ctm.gg/discord).
    """
    aliases = ("ctm",)
    supported_platforms = (Platform.TWITCH,)
    usage = "ctm"
    section = DocSection.OTHER

    def execute(self):
        self.send_message("Join the Classic Tetris Monthly Discord server to learn more about CTM! "
                          "https://go.ctm.gg/discord")


