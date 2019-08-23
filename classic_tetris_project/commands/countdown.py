import time
from random import randint

from .command import Command, CommandException, register_command
from ..util import Platform

@register_command(
    *map(str, range(3, 11)),
    platforms=(Platform.TWITCH,)
)
class Countdown(Command):
    def execute(self):
        self.check_public()
        self.check_moderator()

        n = int(self.context.command_name)
        for i in range(n, 0, -1):
            self.send_message(str(i))
            time.sleep(1)
            
        if random.randint(1,100) == 42:
            self.send_message("Texas!")
        else:
            self.send_message("Tetris!")
