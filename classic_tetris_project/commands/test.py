from .command import Command, register_command

@register_command("test", "devtest")
class TestCommand(Command):
    usage = "test"

    def execute(self):
        self.send_message("Test!")
