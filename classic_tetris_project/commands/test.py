from .command import Command, ArgException, register_command

@register_command("test", "devtest")
class TestCommand(Command):
    async def execute(self):
        await self.send_message("Test!")