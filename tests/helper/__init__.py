from contextlib import contextmanager
from django.test import TestCase
from expects import *
from unittest.mock import patch

from classic_tetris_project.commands.command_context import *
from classic_tetris_project.models import *
from classic_tetris_project.util.memo import memoize, lazy
from .factories import *
from .discord import *
from .twitch import *
from classic_tetris_project import twitch



@contextmanager
def describe(description):
    """
    noop, just used to provide structure to test classes
    """
    yield


class CommandTestCase(TestCase):
    def setUp(self):
        self._patches = [
            patch.object(DiscordCommandContext, "log"),
            patch.object(TwitchCommandContext, "log"),
            patch.object(twitch.APIClient, "_request", side_effect=Exception("twitch API called")),
        ]

        for _patch in self._patches:
            _patch.start()

    def tearDown(self):
        for patch in self._patches:
            patch.stop()

    def expect_discord(self, command, expected_outputs):
        self.discord_api_user.send(self.discord_channel, command)
        expect(self.discord_channel.poll()).to(contain_exactly(*expected_outputs))

    def expect_twitch(self, command, expected_outputs):
        self.twitch_api_user.send(self.twitch_channel, command)
        expect(self.twitch_channel.poll()).to(contain_exactly(*expected_outputs))

    @lazy
    def discord_api_user(self):
        return MockDiscordAPIUser.create()

    @lazy
    def discord_user(self):
        return self.discord_api_user.create_discord_user()

    @lazy
    def discord_channel(self):
        return MockDiscordChannel()

    @lazy
    def twitch_api_user(self):
        return MockTwitchAPIUser.create()

    @lazy
    def twitch_user(self):
        return self.twitch_api_user.create_twitch_user()

    @lazy
    def twitch_channel(self):
        channel_user = MockTwitchAPIUser.create()
        channel_user.create_twitch_user()
        return MockTwitchChannel(channel_user.username)
