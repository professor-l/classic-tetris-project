import factory

from classic_tetris_project.commands.command_context import TwitchCommandContext
from .factories import TwitchUserFactory


class MockTwitchClient:
    def __init__(self):
        self.username = "ClassicTetrisBot"
        self.user_id = "bot_id"
        self._user_id_cache = {}
        self._username_cache = {}

    def get_user(self, user_id):
        return self._user_id_cache.get(user_id)

    def create_user(self, **params):
        if "user_id" in params and params["user_id"] in self._user_id_cache:
            return self._user_id_cache[user_id]
        if "username" in params and params["username"] in self._username_cache:
            return self._username_cache[username]

        user = MockTwitchAPIUser.create(**params)
        self._user_id_cache[user.id] = user
        self._username_cache[user.username] = user
        return user

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
        self.display_name = username

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
    id = factory.Sequence(lambda n: f"mock_{n}")
    username = factory.Sequence(lambda n: f"mock_twitch_user_{n}")


class MockTwitchMessage:
    def __init__(self, author, content, channel):
        self.author = author
        self.content = content
        self.channel = channel
