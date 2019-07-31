from .command import Command, CommandException, register_command

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
