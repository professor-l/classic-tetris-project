import re
from .command import Command, CommandException, register_command
from ..util import Platform
from ..models.users import DiscordUser, TwitchUser

@register_command("pb", "getpb")
class GetPBCommand(Command):
    usage = "pb [username] (default username you)"

    def execute(self, username=None):
        if self.context.platform == Platform.DISCORD:
            platform_user = (self.discord_user_from_username(username) if username
                             else self.context.platform_user)
        elif self.context.platform == Platform.TWITCH:
            platform_user = (self.twitch_user_from_username(username) if username
                             else self.context.platform_user)


        if platform_user:
            user = platform_user.user
            self.send_message("{user_tag} has a pb of {pb:,}".format(
                user_tag=platform_user.user_tag,
                pb=user.ntsc_pb
            ))
        else:
            self.send_message("User has not set a PB.")

    def discord_user_from_username(self, username):
        match = re.match(r"^<@!?(\d+)>$", username)

        if match:
            discord_id = match.group(1)
            try:
                return DiscordUser.objects.get(discord_id=discord_id)
            except DiscordUser.DoesNotExist:
                return None
        else:
            raise CommandException("Invalid username", send_usage=False)

    def twitch_user_from_username(self, username):
        match = re.match(r"^@?(\w+)$", username)

        if match:
            username = match.group(1)
            try:
                return TwitchUser.from_username(username)
            except TwitchUser.DoesNotExist:
                return None
        else:
            raise CommandException("Invalid username", send_usage=False)
