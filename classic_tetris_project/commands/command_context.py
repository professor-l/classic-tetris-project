import re
from .command import COMMAND_MAP
from ..util import Platform

class CommandContext:
    def __init__(self, content):
        self.content = content
        trimmed = re.sub(r"\s+", " ", content).strip()
        tokens = trimmed[len(self.PREFIX):].split(" ")
        self.command_name = tokens[0].lower()
        self.args = tokens[1:]

    async def dispatch(self):
        command_class = COMMAND_MAP.get(self.command_name)
        if command_class:
            command = command_class(self)
            await command.check_support_and_execute()
        else:
            await self.send_message("Not a valid command")

    @classmethod
    def is_command(cls, message):
        return message.startswith(cls.PREFIX)



class DiscordCommandContext(CommandContext):
    PLATFORM = Platform.DISCORD
    PREFIX = "!"
    def __init__(self, message):
        super().__init__(message.content)

        self.message = message
        self.channel = message.channel
        self.author = message.author

    async def send_message(self, message):
        await self.channel.send(message)