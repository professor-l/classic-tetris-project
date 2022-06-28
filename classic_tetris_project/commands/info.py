from .command import Command

COMMANDS_URL = "https://github.com/professor-l/classic-tetris-project/blob/master/docs/COMMANDS.md"
SOURCECODE_URL = "https://github.com/professor-l/classic-tetris-project"

@Command.register("help", "commands", usage="help")
class HelpCommand(Command):
    def execute(self, *args):
        self.send_message(f"All available commands are documented at {COMMANDS_URL}")

@Command.register("code", "source", "sourcecode", usage="source")
class SourceCodeCommand(Command):
    def execute(self, *args):
        self.send_message(f"The source code for this bot can be found here: {SOURCECODE_URL}")

@Command.register("stencil", usage="stencil")
class StencilCommand(Command):
    def execute(self, *args):
        self.send_message("The stencil helps the streamer line up your Tetris playfield with their "
                          "broadcast scene. Link here: https://go.ctm.gg/stencil")

@Command.register_twitch("ctm", usage="ctm")
class CTMDiscordCommand(Command):
    def execute(self, *args):
        self.send_message("Join the Classic Tetris Monthly Discord server to learn more about CTM! "
                          "https://go.ctm.gg/discord")


