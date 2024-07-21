from .command import Command, COMMAND_MAP, CommandException
from ..util import Platform, DocSection
from ..util.docs import parse_docstring

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

    def execute(self, *args):
        if not args:
            self.send_message(f"All available commands are documented at {COMMANDS_URL}")
            return
        cmd_name: str = args[0]
        if cmd_name in COMMAND_MAP:
            cmd = COMMAND_MAP[cmd_name]
            if self.context.platform == Platform.DISCORD:
                usage_str = f"**Usage**: `!{cmd.usage}`"
                platform_list = ", ".join(p.display_name() for p in cmd.supported_platforms)
                platform_str = f"**Platforms**: `{platform_list}`"
                assert cmd.__doc__ is not None
                docs = parse_docstring(cmd.__doc__)
                self.send_message(f"{usage_str}\n{platform_str}\n{docs}")
            elif self.context.platform == Platform.TWITCH:
                # usage_str = f"Usage: !{cmd.usage}"
                # platform_list = ", ".join(p.display_name() for p in cmd.supported_platforms)
                # platform_str = f"Platforms: `{platform_list}`"
                assert cmd.__doc__ is not None
                docs = parse_docstring(cmd.__doc__).split('\n')[0]
                # self.send_message(f"{usage_str}")
                # self.send_message(f"{platform_str}")
                self.send_message(f"{docs}")
        else:
            raise CommandException("Command not found.")

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


