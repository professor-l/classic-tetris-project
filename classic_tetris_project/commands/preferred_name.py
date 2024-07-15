from .command import Command, CommandException
from ..util import Platform, DocSection

@Command.register()
class GetPreferredNameCommand(Command):
    """
    Prints the specified user's preferred name, or yours if no argument is
    provided.
    """
    aliases = ("name", "getname")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "name [username] (default username you)"
    section = DocSection.USER

    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)

        if platform_user and platform_user.user.preferred_name:
            self.send_message("{user_tag} goes by {preferred_name}".format(
                user_tag=platform_user.user_tag,
                preferred_name=platform_user.user.preferred_name
            ))
        else:
            self.send_message("User has not set a preferred name.")


@Command.register()
class SetPreferredNameCommand(Command):
    """
    Sets your preferred name. Can contain letters, numbers, spaces, hyphens,
    underscores, and periods.
    """
    aliases = ("setname",)
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "setname <name>"
    section = DocSection.USER

    def execute(self, *name):
        name = " ".join(name)
        if self.context.user.set_preferred_name(name):
            self.send_message(f"Your preferred name is set to \"{name}\".")

        else:
            raise CommandException("Invalid name. Valid characters are "
                "letters, numbers, spaces, dashes, underscores, and periods.")
