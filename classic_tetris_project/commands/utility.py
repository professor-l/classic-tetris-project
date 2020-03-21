import random
from django.core.cache import cache
from asgiref.sync import async_to_sync
from datetime import datetime

from .command import Command
from ..models.coin import Side
from ..util import Platform
from ..discord import guild_id
from ..words import words

COIN_FLIP_TIMEOUT = 10

HEADS = 0
TAILS = 1
SIDE = 2
COIN_MESSAGES = {
    HEADS: "Heads!",
    TAILS: "Tails!",
    SIDE: "Side o.O"
}

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
        if self.context.platform == Platform.TWITCH:
            self.check_moderator()
        elif (self.context.message.guild and self.context.message.guild.id == guild_id):
            self.context.platform_user.send_message("Due to abuse, `!flip` has been disabled in the CTM Discord server.")

            async_to_sync(self.context.message.delete)()
            return

        if cache.get(f"flip.{self.context.user.id}"):
            return
        cache.set(f"flip.{self.context.user.id}", True, timeout=COIN_FLIP_TIMEOUT)

        o = [HEADS, TAILS, SIDE]
        w = [0.4995, 0.4995, 0.001]
        choice = random.choices(o, weights=w, k=1)[0]

        self.send_message(COIN_MESSAGES[choice])
        if choice == SIDE:
            Side.log(self.context.user)


@Command.register_discord("utc", "time", usage="utc")
class UTCCommand(Command):
    def execute(self, *args):
        t = datetime.utcnow()
        l1 = t.strftime("%A, %b %d")
        l2 = t.strftime("%H:%M (%I:%M %p)")
        self.send_message(f"Current date/time in UTC:\n**{l1}**\n**{l2}**")


@Command.register_discord("authhelp", usage="authhelp")
class AuthHelpCommand(Command):
    AUTH_HELP_STRING = (
        "Qualification authentication is a new feature of this bot. "
        "To generate a random 6-letter auth word, type `!authword`. "
        "That word will be associated with your account for 2 hours. "
        "Calling `!authword` again on any platform will return the same "
        "word. It is used for authenticating qualification attempts. "
        "You should **put the word you're assigned on the leaderboard** "
        "when you complete your first game over 5000 points. This proves "
        "that you're not playing a pre-recorded VOD.\n"
        "**NOTE:** After invoking this command, you will be barred from "
        "doing so for 48 hours. If the qualification attempt falls "
        "through due to extenuating circumstances, you will need to wait "
        "two full days before making another attempt."
    )
    def execute(self, *args):
        self.send_message(self.AUTH_HELP_STRING)


@Command.register_discord("auth", usage="auth")
class WordCommand(Command):
    def execute(self, *args):
        pass
