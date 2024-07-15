import random
import re
from django.core.cache import cache
from discord import Embed
from datetime import datetime

from .command import Command, CommandException
from ..models import Side, TwitchChannel
from ..util import Platform, DocSection
from ..discord import GUILD_ID, client as discord_client
from..util.fieldgen.hz_simulation import HzSimulation
from ..words import Words


COIN_FLIP_TIMEOUT = 10

HEADS = 0
TAILS = 1
SIDE = 2
COIN_MESSAGES = {
    HEADS: "Heads!",
    TAILS: "Tails!",
    SIDE: "Side o.O"
}

@Command.register()
class HzCommand(Command):
    """
    For the given level, provides the approximate tapping speed(s) required to
    clear a given height with the number of taps required.
    """
    aliases = ("hz", "hydrant")
    supported_platforms = (Platform.DISCORD,) # TODO: twitch support
    usage = "hz <level> <height> <taps>"
    section = DocSection.UTIL

    def execute(self, level, height, taps):
        try:
            level = int(level)
            height = int(height)
            taps = int(taps)
        except ValueError:
            raise CommandException(send_usage = True)
        
        try:
            hz = HzSimulation(level,height,taps)
        except ValueError as e:
            raise CommandException(str(e))
                 
        rate = hz.hertz()
        msg = "{tps} taps {hght} high on level {lvl}:\n{mini} - {maxi} Hz\n".format(
            tps=hz.taps,
            hght=hz.height,
            lvl=hz.level,
            mini=rate[0],
            maxi=rate[1]
            )

        # Eagerly cache the image instead of letting the web server handle it lazily
        hz.cache_image()

        printable_sequence = hz.printable_sequence()
        if len(printable_sequence) <= 49:
            msg += "Sample input sequence: {seq}".format(seq=printable_sequence)
        else:
            msg += "Sample sequence too long. (GIF will not animate)"

        msg = "```"+msg+"```"

        embed = Embed().set_image(url=hz.image_url)
        self.send_message_full(self.context.channel.id, msg, embed=embed)

@Command.register()
class SeedGenerationCommand(Command):
    """
    Prints a random 6-digit hex code, used for same piece set matches. Seeds
    which are known to generate bad (i.e. repetitive) piece sequences are
    excluded.
    """
    aliases = ("seed", "hex")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "seed"
    section = DocSection.UTIL

    def execute(self, *args):
        if self.context.platform == Platform.TWITCH:
            self.check_moderator()

        seed = 0
        while (seed % 0x100 < 0x3):
            seed = random.randint(0x200, 0xffffff)
        seed_hex_string = ("%06x" % seed).upper()
        spaced_string = " ".join(re.findall('..', seed_hex_string))
        self.send_message(f"RANDOM SEED: [{spaced_string}]")


@Command.register()
class CoinFlipCommand(Command):
    """
    Prints "Heads!" or "Tails!" randomly. Note: this command has a 10 second
    timeout to avoid spamming.
    """
    aliases = ("flip", "coin", "coinflip")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "flip"
    section = DocSection.UTIL

    def execute(self, *args):
        if self.context.platform == Platform.TWITCH:
            self.check_moderator()
        elif (self.context.message.guild and self.context.message.guild.id == GUILD_ID):
            self.context.platform_user.send_message("Due to abuse, `!flip` has been disabled in the CTM Discord server.")

            self.context.delete_message(self.context.message)
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


@Command.register()
class UTCCommand(Command):
    """
    Prints the current date and time in UTC. Used for scheduling matches with
    restreamers and other players.
    """
    aliases = ("utc", "time")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "utc"
    section = DocSection.UTIL

    def execute(self, *args):
        t = datetime.utcnow()
        l1 = t.strftime("%A, %b %d")
        l2 = t.strftime("%H:%M (%I:%M %p)")
        self.send_message(f"Current date/time in UTC:\n**{l1}**\n**{l2}**")


@Command.register()
class StatsCommand(Command):
    """
    Prints basic usage statistics for the bot.
    """
    aliases = ("stats",)
    supported_platforms = (Platform.DISCORD,)
    usage = "stats"
    notes = ("Moderator-only",)
    section = DocSection.UTIL

    def execute(self, *args):
        self.check_moderator()

        guilds = len(discord_client.guilds)
        channels = TwitchChannel.objects.filter(connected=True).count()

        self.send_message(f"I'm in {guilds} Discord servers and {channels} Twitch channels.")

@Command.register()
class AuthWordCommand(Command):
    """
    Prints a randomly-selected word, to prove a game is happening in real-time.
    """
    aliases = ("authword",)
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "authword"
    section = DocSection.UTIL


    def execute(self, *args):
        self.check_moderator()
        word = Words.get_word()
        self.send_message(f"Authword: {word}")
