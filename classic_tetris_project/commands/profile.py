from discord import Embed
from discord.utils import get

from .. import discord #our discord.
from .command import Command, CommandException
from ..countries import countries, THREE_TO_TWO

from ..util.json_template import match_template
    
TEMPLATE = ("""
{{    
    "color": {color},   
    "author": {{
      "name": "{name}",
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
""")

PLAYSTYLE_EMOJI = {
                   "das": "lovedas",
                   "hypertap": "lovetap",
                   "hybrid": "lovehyb"
                 }
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
        name = self.context.display_name(platform_user)
                
        player_icon = self.get_player_icon(name, username)
        color = self.get_color(name, username)

        ntsc_pb = user.ntsc_pb or "Not set"
        ntsc_pb_19 = user.ntsc_pb_19 or "Not set"
        pal_pb = user.pal_pb or "Not set"
        pronouns = user.get_pronouns_display() or "Not set"
        
        playstyle = self.get_playstyle(user)
        country = self.get_country(user)        
        same_pieces = self.get_same_pieces(user)        
        twitch_channel = self.get_twitch(user)       
        
        json_message = match_template(TEMPLATE,
                                      name=name,
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

    def get_player_icon(self, name, username):
        # search for multiple members...
        members = [self.context.guild.get_member_named(n) for n in [name,username]]
        for m in members:
            if m is not None and m.avatar is not None:
                return PLAYER_ICON.format(id=m.id, avatar=m.avatar)
        
        return ""

    def get_color(self, name, username):
        members = [self.context.guild.get_member_named(n) for n in [name,username]]
        for m in members:
            if m is not None and m.color is not None:
                return m.color.value
        
        return 0 # black

    def get_playstyle(self, user):        
        if user.playstyle:
            ps_emoji = get(self.context.guild.emojis,name=PLAYSTYLE_EMOJI[user.playstyle])
            return str(ps_emoji) + " " + user.get_playstyle_display()
        else:
            return "Not set"

    def get_country(self, user):
        if user.country:
            emoji = ":flag_{}:".format(THREE_TO_TWO[user.country].lower())
            return emoji + " " + countries[user.country]
        return "Not set"

    def get_same_pieces(self, user):
        if user.same_piece_sets:
            check = str(get(self.context.guild.emojis, name="tetrischeck") or ":green_square:")
            return (check + " Yes")
        else:
            cross = str(get(self.context.guild.emojis, name="tetrisx") or ":red_square:")
            return (cross + " No")

    def get_twitch(self, user):
        if hasattr(user, "twitch_user"):
            return f"https://www.twitch.tv/{user.twitch_user.username}"
        return "Not `!link`ed"