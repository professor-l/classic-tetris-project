import random
from django.core.cache import cache
from asgiref.sync import async_to_sync
from datetime import datetime

from .command import Command
from ..models.coin import Side
from ..util import Platform
from ..discord import guild_id

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


@Command.register_discord("utc", usage="utc")
class UTCCommand(Command):
    def execute(self, *args):
        t = datetime.utcnow()
        l1 = t.strftime("%A, %b %d")
        l2 = t.strftime("%H:%M (%I:%M %p)")
        self.send_message(f"Current date/time in UTC:\n**{l1}**\n**{l2}**")
