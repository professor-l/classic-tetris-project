from discord import Embed
from discord.utils import get

from ..discord import *
from .command import Command, CommandException
from ..countries import Country

from ..util import Platform
from ..util.json_template import match_template

DISCORD_TEMPLATE = ("""
{{
    "color": {color},
    "author": {{
      "name": "{name}",
      "url": "{url}",
      "icon_url": "{player_icon}"
    }},
    "fields": [
      {{
        "name": "Personal Bests",
        "value": "```NTSC: {ntsc_pb} \\nNTSC(19): {ntsc_pb_19}\\nNTSC(29): {ntsc_pb_29}\\nPAL: {pal_pb}```\\n"
      }},
      {{
        "name": "Pronouns",
        "value": "{pronouns}",
        "inline": "True"
      }},
      {{
        "name": "Playstyle",
        "value": "{playstyle}",
        "inline": "True"
      }},
      {{
        "name": "Country",
        "value": "{country}",
        "inline": "True"
      }},
      {{
        "name": "Same piece sets",
        "value": "{same_pieces}",
        "inline": "True"
      }},
      {{
        "name": "Twitch",
        "value": "{twitch_channel}"
      }}]
}}
""")

TWITCH_TEMPLATE = "{username}'s profile. NTSC PBs: {ntsc_pb} overall, {ntsc_pb_19} on 19, {ntsc_pb_29} on 29. PAL PB: {pal_pb}. Pronouns: {pronouns}. Playstyle: {playstyle}. Country: {country}. SPS: {sps}."

PLAYSTYLE_EMOJI = {
                   "das": "lovedas",
                   "hypertap": "lovetap",
                   "hybrid": "lovehyb",
                   "roll": "loveroll"
                 }

TETRIS_X = "tetrisx"
TETRIS_CHECK = "tetrischeck"

PLAYER_ICON = "https://cdn.discordapp.com/avatars/{id}/{avatar}.jpg"

@Command.register("profile", usage="profile [username] (default username you)")
class ProfileCommand(Command):

    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        if username and not self.any_platform_user_from_username(username):
            raise CommandException("Specified user has no profile.")

        platform_user = (self.any_platform_user_from_username(username) if username
                         else self.context.platform_user)

        if not platform_user:
            raise CommandException("Invalid specified user.")

        if self.context.platform == Platform.DISCORD:
            self.execute_discord(platform_user)
        elif self.context.platform == Platform.TWITCH:
            self.execute_twitch(platform_user)

    def execute_discord(self, platform_user):
        user = platform_user.user
        guild_id = self.context.guild.id if self.context.guild else None
        try:
            member = platform_user.get_member(guild_id)
        except AttributeError:
            member = None

        name = self.context.display_name(platform_user)
        player_icon = self.get_player_icon(member)
        color = self.get_color(member)
        url=user.get_absolute_url(True)

        ntsc_pb = self.format_pb(user.get_pb("ntsc")).rjust(13)
        ntsc_pb_19 = self.format_pb(user.get_pb("ntsc", 19)).rjust(9)
        ntsc_pb_29 = self.format_pb(user.get_pb("ntsc", 29)).rjust(9)
        pal_pb = self.format_pb(user.get_pb("pal")).rjust(14)

        pronouns = user.get_pronouns_display() or "Not set"

        playstyle = self.get_playstyle(user)
        country = self.get_country(user)
        same_pieces = self.get_same_pieces(user)
        twitch_channel = self.get_twitch(user)

        json_message = match_template(DISCORD_TEMPLATE,
                                      name=name,
                                      url=url,
                                      color=color,
                                      player_icon=player_icon,
                                      ntsc_pb=ntsc_pb,
                                      ntsc_pb_19=ntsc_pb_19,
                                      ntsc_pb_29=ntsc_pb_29,
                                      pal_pb=pal_pb,
                                      pronouns=pronouns,
                                      playstyle=playstyle,
                                      country=country,
                                      same_pieces=same_pieces,
                                      twitch_channel=twitch_channel)

        e = Embed.from_dict(json_message)
        self.send_message_full(self.context.channel.id, embed=e)

    def execute_twitch(self, platform_user):
        user = platform_user.user

        username = self.context.display_name(platform_user)
        ntsc_pb = self.format_pb(user.get_pb("ntsc"))
        ntsc_pb_19 = self.format_pb(user.get_pb("ntsc", 19))
        ntsc_pb_29 = self.format_pb(user.get_pb("ntsc", 29))
        pal_pb = self.format_pb(user.get_pb("pal"))
        pronouns = user.get_pronouns_display() or "Not set"
        playstyle = user.get_playstyle_display() or "Not set"
        country = "Not set"
        if user.country is not None:
            country = Country.get_country(user.country).full_name
        sps = "Yes" if user.same_piece_sets else "No"

        profile_message = TWITCH_TEMPLATE.format(
            username=username,
            ntsc_pb=ntsc_pb,
            ntsc_pb_19=ntsc_pb_19,
            ntsc_pb_29=ntsc_pb_29,
            pal_pb=pal_pb,
            pronouns=pronouns,
            playstyle=playstyle,
            country=country,
            sps=sps,
        )
        self.send_message(profile_message)

    def format_pb(self, value):
        if value:
            return "{pb:,}".format(pb=value)
        else:
            return "Not set"

    def get_player_icon(self, member):

        if member is not None and member.avatar is not None:
            return PLAYER_ICON.format(id=member.id, avatar=member.avatar)

        return ""

    def get_color(self, member):
        if member is not None and member.color is not None:
            return member.color.value

        return 0 # black

    def get_playstyle(self, user):
        if user.playstyle:
            emote = get_emote(PLAYSTYLE_EMOJI[user.playstyle])
            display = user.get_playstyle_display()
            return (emote + " " + display) if emote else display
        else:
            return "Not set"

    def get_country(self, user):
        if user.country is not None:
            country = Country.get_country(user.country)
            return country.get_flag() + " " + country.full_name
        return "Not set"

    def get_same_pieces(self, user):
        if user.same_piece_sets:
            emote = get_emote(TETRIS_CHECK)
            return (emote + " Yes") if emote else "Yes"
        else:
            emote = get_emote(TETRIS_X)
            return (emote + " No") if emote else "No"

    def get_twitch(self, user):
        if hasattr(user, "twitch_user"):
            return f"https://www.twitch.tv/{user.twitch_user.username}"
        return "Not linked (head to go.ctm.gg)"
