from .command import Command
from ..util import Platform

COMMANDS_URL = "https://github.com/professor-l/classic-tetris-project/blob/master/COMMANDS.md"

@Command.register("help",
                  usage="help")
class HelpCommand(Command):
    def execute(self, *args):
        self.send_message(f"All available commands are documented at {COMMANDS_URL}")
