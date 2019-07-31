from .command import Command, CommandException, register_command
from ..util import Platform

@register_command("name", "getname")
class GetPreferredNameCommand(Command):
    usage = "name [username] (default username you)"

    def execute(self, username=None):
        if username is None:
            platform_user = self.context.platform_user
        elif self.context.platform == Platform.DISCORD:
            platform_user = Command.discord_user_from_username(username)
        elif self.context.platform == Platform.TWITCH:
            platform_user = Command.twitch_user_from_username(username)

        if platform_user and platform_user.user.preferred_name:
            self.send_message("{user_tag} goes by {preferred_name}".format(
                user_tag=platform_user.user_tag,
                preferred_name=platform_user.user.preferred_name
            ))
        else:
            self.send_message("User has not set a preferred name.")


@register_command("setname")
class SetPreferredNameCommand(Command):
    usage = "setname <name>"

    def execute(self, *name):
        name = " ".join(name)
        if self.context.user.set_preferred_name(name):
            self.send_message(f"Your preferred name is set to \"{name}\".")

        else:
            raise CommandException("Invalid name. Valid characters are "
                "letters, numbers, spaces, dashes, underscores, and periods.")
