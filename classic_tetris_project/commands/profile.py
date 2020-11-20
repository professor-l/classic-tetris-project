from discord import Embed
from discord.utils import get

from ..discord import *
from .command import Command, CommandException
from ..countries import Country

from ..util.json_template import match_template

TEMPLATE = ("""
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
        "value": "```NTSC: {ntsc_pb} \\nNTSC(19): {ntsc_pb_19}\\nPAL: {pal_pb}```\\n"
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
        "name": "Same Piece sets",
        "value": "{same_pieces}",
        "inline": "True"
      }},
      {{
        "name": "Twitch",
        "value": "{twitch_channel}"
      }}]
}}
""")

PLAYSTYLE_EMOJI = {
                   "das": "lovedas",
                   "hypertap": "lovetap",
                   "hybrid": "lovehyb"
                 }

TETRIS_X = "tetrisx"
TETRIS_CHECK = "tetrischeck"

PLAYER_ICON = "https://cdn.discordapp.com/avatars/{id}/{avatar}.jpg"

@Command.register_discord("profile",
                  usage="profile [username] (default username you)")
class ProfileCommand(Command):

    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        if username and not self.any_platform_user_from_username(username):
            raise CommandException("Specified user has no profile.")

        platform_user = (self.any_platform_user_from_username(username) if username
                         else self.context.platform_user)

        if not platform_user:
            raise CommandException("Invalid specified user.")

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
        pal_pb = self.format_pb(user.get_pb("pal")).rjust(14)

        pronouns = user.get_pronouns_display() or "Not set"

        playstyle = self.get_playstyle(user)
        country = self.get_country(user)
        same_pieces = self.get_same_pieces(user)
        twitch_channel = self.get_twitch(user)

        json_message = match_template(TEMPLATE,
                                      name=name,
                                      url=url,
                                      color=color,
                                      player_icon=player_icon,
                                      ntsc_pb=ntsc_pb,
                                      ntsc_pb_19=ntsc_pb_19,
                                      pal_pb=pal_pb,
                                      pronouns=pronouns,
                                      playstyle=playstyle,
                                      country=country,
                                      same_pieces=same_pieces,
                                      twitch_channel=twitch_channel)

        e = Embed.from_dict(json_message)
        self.send_message_full(self.context.channel.id, embed=e)

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
        return "Not linked (head to ctm.gg)"
