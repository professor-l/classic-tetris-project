from .command import Command, CommandException, register_command
from ..util import Platform

@register_command("name", "getname")
class GetPreferredNameCommand(Command):
    usage = "name [username] (default username you)"

    def execute(self, username=None):
        if self.context.platform == Platform.DISCORD:
            platform_user = (Command.discord_user_from_username(username) if username
                             else self.context.platform_user)
        elif self.context.platform == Platform.TWITCH:
            platform_user = (Command.twitch_user_from_username(username) if username
                             else self.context.platform_user)

        if not platform_user or not platform_user.user.preferred_name:
            self.send_message("User has not set a preferred name.")
            return
        
        self.send_message("{user_tag} goes by {preferred_name}".format(
            user_tag=platform_user.user_tag,
            preferred_name=platform_user.user.preferred_name
        ))
