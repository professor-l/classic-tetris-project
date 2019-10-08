from .command import Command, CommandException

@Command.register("name", "getname",
                  usage="name [username] (default username you)")
class GetPreferredNameCommand(Command):
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


@Command.register("setname",
                  usage="setname <name>")
class SetPreferredNameCommand(Command):
    def execute(self, *name):
        name = " ".join(name)
        if self.context.user.set_preferred_name(name):
            self.send_message(f"Your preferred name is set to \"{name}\".")

        else:
            raise CommandException("Invalid name. Valid characters are "
                "letters, numbers, spaces, dashes, underscores, and periods.")
