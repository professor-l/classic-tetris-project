from discord import Embed
from discord.utils import get as get_emoji

from .. import discord #our discord.
from .command import Command, CommandException
from ..countries import countries, THREE_TO_TWO

from ..util.json_template import match_template

TEMPLATE = (
"""
{{    
    "title": "{name}",
    "description": "",
    "url": "https://github.com/professor-l/classic-tetris-project/",
    "color": 10768969,   
    "author": {{
      "url": "https://github.com/professor-l/classic-tetris-project/",
      "icon_url": "{player_icon}"
    }},
    "fields": [
      {{
        "name": "Personal Bests",
        "value": "NTSC: {ntsc_pb} \\n NTSC(19): {ntsc_pb_19}\\n PAL: {pal_pb}\\n"
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
"""
)

PLAYSTYLE_EMOJI = {
                   "das": "lovedas",
                   "hypertap": "lovetap",
                   "hybrid": "lovehyb"
                 }
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
        name = self.context.display_name(platform_user)

        ntsc_pb = user.ntsc_pb or "Not set"
        ntsc_pb_19 = user.ntsc_pb_19 or "Not set"
        pal_pb = user.pal_pb or "Not set"
        pronouns = user.get_pronouns_display() or "Not set"
        

        ps_emoji = None
        if user.playstyle:
            ps_emoji = get_emoji(self.context.guild.emojis,name=PLAYSTYLE_EMOJI[user.playstyle])
                
        ps_emoji = str(ps_emoji) + " " if ps_emoji else ""
        playstyle = ps_emoji + (user.get_playstyle_display() or "Not set")
        
        if user.country:
            emoji = ":flag_{}:".format(THREE_TO_TWO[user.country].lower())
            country = emoji + " " + countries[user.country]
        else:
            countr = "Not set"

        
        check = str(get_emoji(self.context.guild.emojis,name="tetrischeck") or ":green_square:")
        cross = str(get_emoji(self.context.guild.emojis,name="tetrisx") or ":red_square:")

        same_pieces = (check + " Yes") if user.same_piece_sets else (cross + " No")

        if hasattr(user, "twitch_user"):
            twitch_channel = f"https://www.twitch.tv/{user.twitch_user.username}"
        else:
            twitch_channel = ":twitch: Not `!link`ed"

        json_message = match_template(TEMPLATE,
                                      name=name,
                                      player_icon='',
                                      ntsc_pb=ntsc_pb,
                                      ntsc_pb_19=ntsc_pb_19,
                                      pal_pb=pal_pb,
                                      pronouns=pronouns,
                                      playstyle=playstyle,
                                      country=country,
                                      same_pieces=same_pieces,
                                      twitch_channel=twitch_channel
                                     )        

        e = Embed.from_dict(json_message)
        self.send_message_full(self.context.channel.id, embed=e)



