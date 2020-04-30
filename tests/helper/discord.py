import factory

from classic_tetris_project.commands.command_context import DiscordCommandContext
from ..factories import DiscordUserFactory


class MockDiscordChannel:
    def __init__(self, name="mock"):
        self.sent_messages = []
        self.name = name

    async def send(self, message):
        self.sent_messages.append(message)

    def poll(self):
        # Convenience method for taking the latest messages sent since the last poll
        messages = self.sent_messages
        self.sent_messages = []
        return messages


class MockDiscordAPIUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def send(self, channel, content):
        message = MockDiscordMessage(self, content, channel)
        context = DiscordCommandContext(message)
        context.dispatch()

    def create_discord_user(self):
        return DiscordUserFactory(discord_id=self.id,
                                  username=self.name)

    @staticmethod
    def create(*args, **kwargs):
        return MockDiscordAPIUserFactory(*args, **kwargs)

class MockDiscordAPIUserFactory(factory.Factory):
    class Meta:
        model = MockDiscordAPIUser
    id = factory.Sequence(lambda n: f"{n}")
    name = factory.Sequence(lambda n: f"Mock Discord User {n}")


class MockDiscordMessage:
    def __init__(self, author, content, channel, guild=None):
        self.author = author
        self.content = content
        self.channel = channel
        self.guild = guild
