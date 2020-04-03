from .. import discord

from .command import Command, CommandException
from ..countries import countries

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
        playstyle = user.get_playstyle_display() or "Not set"
        country = countries[user.country] if user.country else "Not set"
        same_pieces = "Yes" if user.same_piece_sets else "No"

        if hasattr(user, "twitch_user"):
            twitch_channel = f"https://www.twitch.tv/{user.twitch_user.username}"
        else:
            twitch_channel = "Not set"


        self.send_message(
            ("**{name}'s profile:**\n\n"
             "    **Personal bests:**\n"
             "        NTSC: {ntsc_pb}\n"
             "        NTSC (19): {ntsc_pb_19}\n"
             "        PAL: {pal_pb}\n"
             "    **Pronouns:** {pronouns}\n"
             "    **Playstyle:** {playstyle}\n"
             "    **Country:** {country}\n"
             "    **Same Piece Sets:** {same_pieces}\n"
             "    **Twitch:** {twitch_channel}"
             ).format(
                 name=name,
                 ntsc_pb=ntsc_pb,
                 ntsc_pb_19=ntsc_pb_19,
                 pal_pb=pal_pb,
                 pronouns=pronouns,
                 playstyle=playstyle,
                 country=country,
                 same_pieces=same_pieces,
                 twitch_channel=twitch_channel
            )
        )

