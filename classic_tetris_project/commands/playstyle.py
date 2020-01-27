from .command import Command, CommandException

@Command.register("setplaystyle", "setstyle",
                  usage="setplaystyle <DAS|Hypertap|Hybrid>")
class SetPlaystyleCommand(Command):
    def execute(self, style):
        if self.context.user.set_playstyle(style):
            self.send_message(f"Your playstyle is now {self.context.user.get_playstyle_display()}!")
        else:
            raise CommandException("Invalid playstyle. Valid playstyles: DAS, Hypertap, Hybrid.")
