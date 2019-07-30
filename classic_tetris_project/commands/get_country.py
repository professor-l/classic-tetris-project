from .command import Command, CommandException, register_command
from ..util import Platform
from ..countries import countries

@register_command("country", "getcountry")
class GetCountryCommand(Command):
    usage = "country [username] (default username you)"

    def execute(self, username=None):
        if self.context.platform == Platform.DISCORD:
            platform_user = (Command.discord_user_from_username(username) if username
                             else self.context.platform_user)
        elif self.context.platform == Platform.TWITCH:
            platform_user = (Command.twitch_user_from_username(username) if username
                             else self.context.platform_user)

        if not platform_user or not platform_user.user.country:
            self.send_message("User has not set a country.")
            return

        self.send_message("{user_tag} is from {country}!".format(
            user_tag = platform_user.user_tag,
            country=countries[platform_user.user.country]
        ))
