from ..util import Platform

class ArgException(Exception):
    pass


class Command:
    def __init__(self, context):
        self.context = context
        self.args = context.args

    @property
    def supported_platforms(self):
        return [Platform.DISCORD, Platform.TWITCH]



    async def check_support_and_execute(self):
        if self.context.PLATFORM in self.supported_platforms:
            try:
                await self.execute(*self.args)
            except ArgException:
                await self.send_usage()
        else:
            await self.send_message("Command not supported on this platform.")

    async def send_message(self, message):
        await self.context.send_message(message)

    async def send_usage(self):
        # Add `wrapper` if in Discord
        formatted = self.context.format_code("{prefix}{usage}".format(
            prefix=self.context.PREFIX,
            usage=self.usage
        ))
        await self.send_message("Usage: {formatted}".format(formatted=formatted))




COMMAND_MAP = {}

def register_command(*aliases):
    def register(command):
        for alias in aliases:
            COMMAND_MAP[alias] = command
        return command
    return register