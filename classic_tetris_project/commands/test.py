from .command import Command

@Command.register("test", "devtest",
                  usage="test")
class TestCommand(Command):
    def execute(self):
        self.send_message("Test!")
