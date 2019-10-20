from .command import Command
from ..util import Platform

COMMANDS_URL = "https://github.com/professor-l/classic-tetris-project/blob/master/COMMANDS.md"

@Command.register("help", usage="help")
class HelpCommand(Command):
    def execute(self, *args):
        self.send_message(f"All available commands are documented at {COMMANDS_URL}")


@Command.register("stencil", usage="stencil")
class StencilCommand(Command):
    def execute(self, *args):
        self.send_message("The stencil helps the streamer line up your Tetris playfield with their "
                          "broadcast scene. Link here: http://bit.ly/TheStencil")

@Command.register_twitch("ctm", usage="ctm")
class CTMDiscordCommand(Command):
    def execute(self, *args):
        self.send_message("Join the Classic Tetris Monthly Discord server to learn more about CTM! https://discord.gg/SYP37aV")


@Command.register("leaderboard", usage="leaderboard")
class CTWCLeaderboardCommmand(Command):
    def execute(self, *args):
        self.send_message("CTWC qualification leaderboard: https://bit.ly/CTWC2019Leaderboard")

@Command.register("bracket", usage="bracket")
class CTWCBracketCommand(Command):
    def execute(self, *args):
        self.send_message("Round 0 bracket: http://bit.ly/2019CTWCTop32")
