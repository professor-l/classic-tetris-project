import random
from django.core.cache import cache
from discord import ChannelType

from .command import Command, CommandException, register_command
from ..util import Platform
from ..models.users import User, DiscordUser, TwitchUser


REQUEST_TIMEOUT = 30 * 60

@register_command(
    "link", "linkaccount", 
    platforms=(Platform.DISCORD,)
)
class LinkCommand(Command):
    usage = "link <twitch username>"

    def execute(self, username):
        if self.context.channel.type != ChannelType.private:
            raise CommandException("This command only works in a direct message.")

        twitch_user = Command.twitch_user_from_username(username)
        if not twitch_user:
            raise CommandException("That twitch user doesn't exist!")
        discord_user = self.context.platform_user

        try:
            linked_discord_user = DiscordUser.objects.get(user_id=twitch_user.user_id)
            raise CommandException(
                f"The twitch user \"{username}\" is linked to the Discord user \"{linked_discord_user.username}\"."
            )
        except DiscordUser.DoesNotExist:
            pass

        try:
            linked_twitch_user = TwitchUser.objects.get(user_id=discord_user.user_id)
            raise CommandException(
                f"You've already linked this Discord account to the twitch account \"{linked_twitch_user.username}\"."
            )
        except TwitchUser.DoesNotExist:
            pass

        
        link_request = cache.get(f"link_requests.{self.context.user.id}")
        if link_request and link_request.target_user_id == twitch_user.user_id:
            raise CommandException(f"You've already sent a link request to the twitch user \"{username}\".")
        
        link_request = LinkRequest(discord_user.user_id, twitch_user.user_id)
        cache.set(f"link_requests.{discord_user.user_id}", link_request, timeout=REQUEST_TIMEOUT)

        twitch_user.send_message(
            f"The Discord user \"{discord_user.username}\" wants to link their Discord account to this twitch account."
        )
        twitch_user.send_message(
            f"Your one-time 6-digit token is {link_request.token}. If you did "
            "not initiate this request, you may ignore this message."
        )

        self.send_message(
            f"A token has been sent to \"{username}\" on twitch. To confirm "
            "this link, type `!linktoken <token>`. The token will expire in "
            "thirty minutes."
        )


@register_command(
    "linktoken",
    platforms=(Platform.DISCORD,)
)
class LinkTokenCommand(Command):
    usage = "linktoken <token>"

    def execute(self, token):
        if self.context.channel.type != ChannelType.private:
            raise CommandException("This command must be run in a direct message.")

        link_request = cache.get(f"link_requests.{self.context.user.id}")

        if link_request and link_request.token == token:
            target_user = User.objects.get(id=link_request.target_user_id)
            twitch_user = TwitchUser.objects.filter(user_id=target_user.id).first()
            self.context.user.link(target_user)

            self.send_message(f"The twitch account \"{twitch_user.username}\" is now linked to this Discord account!")
            self.send_message(f"""
Preferred Name: {self.context.user.preferred_name}
Country: {self.context.user.country}
PB: {self.context.user.ntsc_pb}
PAL PB: {self.context.user.pal_pb}
            """)
            cache.delete(f"link_requests.{self.context.user.id}")
        else:
            raise CommandException("No link request with that token was made.")

@register_command("unlink")
class UnlinkCommand(Command):
    usage = "unlink yesimsure"

    def execute(self, sure=None):
        if sure != "yesimsure":
            raise CommandException(
                "Doing this will unlink this account from any other accounts "
                "it has been linked with through this bot in the past. Data "
                "will be preserved on other platforms. Are you sure?",
                send_usage=True
            )
        
        if self.context.platform == Platform.DISCORD:
            if not TwitchUser.objects.filter(user_id=self.context.user.id).exists():
                raise CommandException("No accounts to unlink!")
            self.context.platform_user.delete()

        elif self.context.platform == Platform.TWITCH:
            if not DiscordUser.objects.filter(user_id=self.context.user.id).exists():
                raise CommandException("No accounts to unlink!")
            self.context.platform_user.delete()
        
        self.send_message("This account has been successfully unlinked from all user data.")

class LinkRequest:
    def __init__(self, request_user_id, target_user_id):
        self.request_user_id = request_user_id
        self.target_user_id = target_user_id
        self.token = "".join(str(random.randrange(10)) for _ in range(6))

