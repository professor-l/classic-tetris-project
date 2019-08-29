import time
from random import randint

from .command import Command, CommandException

@Command.register_twitch(*map(str, range(3, 11)),
                         usage=None)
class Countdown(Command):
    @property
    def usage(self):
        return self.context.command_name

    def execute(self):
        self.check_public()
        self.check_moderator()

        n = int(self.context.command_name)
        for i in range(n, 0, -1):
            self.send_message(str(i))
            time.sleep(1)

        if randint(1,100) == 42:
            self.send_message("Texas!")
        else:
            self.send_message("Tetris!")
