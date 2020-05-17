import factory

from classic_tetris_project.commands.command_context import TwitchCommandContext
from .factories import TwitchUserFactory


class MockTwitchClient:
    def __init__(self):
        self.username = "ClassicTetrisBot"

class MockTwitchChannel:
    def __init__(self, name):
        self.sent_messages = []
        self.name = name
        self.type = "channel"
        self.client = MockTwitchClient()

    def send_message(self, message):
        self.sent_messages.append(message)

    def poll(self):
        # Convenience method for taking the latest messages sent since the last poll
        messages = self.sent_messages
        self.sent_messages = []
        return messages


class MockTwitchAPIUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def send(self, channel, content):
        message = MockTwitchMessage(self, content, channel)
        context = TwitchCommandContext(message)
        context.dispatch()

    def create_twitch_user(self):
        return TwitchUserFactory(twitch_id=self.id,
                                 username=self.username)

    @staticmethod
    def create(*args, **kwargs):
        return MockTwitchAPIUserFactory(*args, **kwargs)

class MockTwitchAPIUserFactory(factory.Factory):
    class Meta:
        model = MockTwitchAPIUser
    id = factory.Sequence(lambda n: f"{n}")
    username = factory.Sequence(lambda n: f"mock_twitch_user_{n}")


class MockTwitchMessage:
    def __init__(self, author, content, channel):
        self.author = author
        self.content = content
        self.channel = channel
