import time
from django.core.cache import cache
from random import randint

from .command import Command, CommandException

MIN_COUNTDOWN = 3
MAX_COUNTDOWN = 10

@Command.register_twitch(*map(str, range(MIN_COUNTDOWN, MAX_COUNTDOWN + 1)),
                         usage=None)
class Countdown(Command):
    @property
    def usage(self):
        return self.context.command_name

    def execute(self):
        self.check_public()
        self.check_moderator()

        n = int(self.context.command_name)
        self.check_validity(n)

        for i in range(n, 0, -1):
            self.send_message(str(i))
            time.sleep(1)

        self.send_message("Texas!" if randint(1,100) == 42 else "Tetris!")

    def check_validity(self, n):
        channel = self.context.channel.name
        if cache.get(f"countdown_in_progress.{channel}") is not None:
            raise CommandException()
        else:
            cache.set(f"countdown_in_progress.{channel}", True, timeout=(n+1))

