import random

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


@Command.register("seed", "hex", usage="seed")
class SeedGenerationCommand(Command):
    def execute(self, *args):
        seed = 0
        while (seed % 0x100 < 0x3):
            seed = random.randint(0x200, 0xffffff)
        self.send_message(("RANDOM SEED: [%06x]" % seed))

@Command.register("coin", "flip", "coinflip", usage="flip")
class CoinFlipCommand(Command):
    def execute(self, *args):
        self.send_message(random.choice(["Heads!", "Tails!"]))
