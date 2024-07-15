import time
from django.core.cache import cache
from random import randint

from .command import Command, CommandException
from ..util import Platform, DocSection

MIN_COUNTDOWN = 3
MAX_COUNTDOWN = 10

@Command.register()
class Countdown(Command):
    """
    Counts down from 3 before saying "Tetris!" in the chat. Works for any
    number from 3-10.

    **Note:** If the bot is not a moderator in your Twitch channel, it will not
    be able to say more than one message per second, and this restriction
    (which is built into Twitch) will interfere with countdowns. You can make
    the bot a moderator by typing `/mod @ClassicTetrisBot` after you have
    `!summon`ed it.
    """
    aliases = tuple(str(i) for i in range(MIN_COUNTDOWN, MAX_COUNTDOWN+1))
    supported_platforms = (Platform.TWITCH,)
    usage = "n (3 <= n <= 10)"
    notes = ("Moderator-only",)
    section = DocSection.OTHER

    def __init__(self, context):
        super().__init__(context)
        self.usage = self.context.command_name

    def execute(self):
        self.check_public()
        self.check_moderator()

        n = int(self.context.command_name)
        self.check_validity(n)

        for i in range(n, 0, -1):
            self.send_message(str(i))
            time.sleep(1)

        s = "Tetris!"
        i = randint(1, 1000)
        if i == 42:
            s = "Tortoise!"
        elif i == 43:
            s = "Texas!"
        elif i == 44:
            s = "Tetris™!"
        elif i == 45:
            s = "I'm contacting you regarding your car's extended warranty."
        self.send_message(s)

    def check_validity(self, n):
        channel = self.context.channel.name
        if cache.get(f"countdown_in_progress.{channel}") is not None:
            raise CommandException()
        else:
            cache.set(f"countdown_in_progress.{channel}", True, timeout=(n+1))

