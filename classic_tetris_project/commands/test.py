from .command import Command, ArgException, register_command

@register_command("test", "devtest")
class TestCommand(Command):
    def execute(self):
        self.send_message("Test!")
