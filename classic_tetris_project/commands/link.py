import random
from django.core.cache import cache
from discord import ChannelType

from .command import Command, CommandException
from ..util import Platform
from ..models.users import User, DiscordUser, TwitchUser
from ..countries import Country


REQUEST_TIMEOUT = 30 * 60

@Command.register_discord("link", "linkaccount",
                          usage="link <twitch username>")
class LinkCommand(Command):
    def execute(self, username):

        twitch_user = Command.twitch_user_from_username(username, existing_only=False)
        if not twitch_user:
            raise CommandException("That twitch user doesn't exist!")
        discord_user = self.context.platform_user

        try:
            linked_discord_user = DiscordUser.objects.get(user_id=twitch_user.user_id)
            raise CommandException(
                f"The twitch user \"{username}\" is linked to the Discord user \"{linked_discord_user.display_name()}\"."
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
            f"The Discord user \"{discord_user.display_name()}\" wants to link their Discord account to this twitch account."
        )
        twitch_user.send_message(
            f"Your one-time 6-digit token is {link_request.token}. If you did "
            "not initiate this request, you may ignore this message."
        )

        self.context.platform_user.send_message(
            f"A token has been sent to \"{username}\" on twitch. To confirm "
            "this link, type `!linktoken <token>`. The token will expire in "
            "thirty minutes."
        )
        self.send_message("I sent you a DM with instructions!")


@Command.register_discord("linktoken",
                          usage="linktoken <token>")
class LinkTokenCommand(Command):
    def execute(self, token):
        self.check_private(sensitive=True)

        link_request = cache.get(f"link_requests.{self.context.user.id}")

        if link_request and link_request.token == token:
            target_user = User.objects.get(id=link_request.target_user_id)
            twitch_user = target_user.twitch_user
            self.context.user.merge(target_user)

            self.send_message(
                f"The twitch account \"{twitch_user.username}\" is now linked to this "
                "Discord account! Try using the `!profile` command to see your profile "
                "information!"
            )
            cache.delete(f"link_requests.{self.context.user.id}")
        else:
            raise CommandException("No link request with that token was made.")


@Command.register("unlink",
                  usage="unlink yesimsure")
class UnlinkCommand(Command):
    def execute(self, sure=None):

        if sure != "yesimsure":
            raise CommandException(
                "Doing this will unlink this account from any other accounts "
                "it has been linked with through this bot in the past. Data "
                "will be preserved on other platforms. Are you sure?",
                send_usage=True
            )

        if self.context.platform == Platform.DISCORD:
            if not hasattr(self.context.user, "twitch_user"):
                raise CommandException("No accounts to unlink!")
            self.context.platform_user.unlink_from_user()

        elif self.context.platform == Platform.TWITCH:
            if not hasattr(self.context.user, "discord_user"):
                raise CommandException("No accounts to unlink!")
            self.context.platform_user.unlink_from_user()

        self.context.platform_user.send_message("This account has been successfully unlinked from all user data.")


class LinkRequest:
    def __init__(self, request_user_id, target_user_id):
        self.request_user_id = request_user_id
        self.target_user_id = target_user_id
        self.token = "".join(str(random.randrange(10)) for _ in range(6))
