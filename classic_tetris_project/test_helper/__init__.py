import itertools
import re
from hamcrest import *
from django.db import transaction, connections
from django.test import override_settings, Client
from django.core.cache import cache
from unittest.mock import patch

from classic_tetris_project.commands.command_context import *
from classic_tetris_project.models import *
from classic_tetris_project.util.memo import memoize, lazy
from .factories import *
from .discord import *
from .twitch import *
from .matchers import *
from classic_tetris_project import discord, twitch


patch.object(twitch.APIClient, "_request", side_effect=Exception("twitch API called")).start()
patch.object(discord.APIClient, "_request", side_effect=Exception("discord API called")).start()


class Spec:
    def setup(self):
        self._setting_override = override_settings(
            TESTING=True,
            DEBUG=True,
            CACHES={
                "default": {
                    "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                }
            },
            CELERY_TASK_EAGER_PROPAGATES=True,
            CELERY_TASK_ALWAYS_EAGER=True,
            CELERY_BROKER_BACKEND="memory",
        )
        self._setting_override.__enter__()

        self._patches = self.patches()
        for patch in self._patches:
            patch.start()

    def patches(self):
        return [
            patch("classic_tetris_project.twitch.client", MockTwitchClient()),
        ]

    def teardown(self):
        cache.clear()

        for patch in self._patches:
            patch.stop()

        self._setting_override.__exit__(None, None, None)

    @lazy
    def current_user(self):
        return UserFactory()

    @lazy
    def current_website_user(self):
        return WebsiteUser.fetch_by_user(self.current_user)

    @lazy
    def current_auth_user(self):
        return self.current_website_user.auth_user

    @lazy
    def client(self):
        return Client()

    def sign_in(self):
        self.client.force_login(self.current_auth_user)

    def get(self, *args, **kwargs):
        return self.client.get(self.url, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(self.url, *args, **kwargs)


class CommandSpec(Spec):
    def patches(self):
        return super().patches() + [
            patch.object(DiscordCommandContext, "log"),
            patch.object(TwitchCommandContext, "log"),
        ]

    def send_discord(self, command, discord_api_user=None, flush=True):
        discord_api_user = discord_api_user or self.discord_api_user
        discord_api_user.send(self.discord_channel, command)
        if flush:
            self.discord_channel.poll()

    def send_twitch(self, command, twitch_api_user=None, flush=True):
        twitch_api_user = twitch_api_user or self.twitch_api_user
        twitch_api_user.send(self.twitch_channel, command)
        if flush:
            self.twitch_channel.poll()

    def assert_discord(self, command, expected_messages):
        self.send_discord(command, flush=False)
        actual_messages = self.discord_channel.poll()
        self._assert_messages(actual_messages, expected_messages)

    def assert_twitch(self, command, expected_messages):
        self.send_twitch(command, flush=False)
        actual_messages = self.twitch_channel.poll()
        self._assert_messages(actual_messages, expected_messages)

    def _assert_messages(self, actual_messages, expected_messages):
        for actual, expected in itertools.zip_longest(actual_messages, expected_messages,
                                                      fillvalue=""):
            if isinstance(expected, str):
                assert_that(actual, equal_to(expected))
            elif isinstance(expected, re.Pattern):
                assert_that(actual, matches_regexp(expected))
            else:
                raise f"Can't match message: {expected}"

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
        return self.twitch_client.create_user()

    @lazy
    def twitch_user(self):
        return self.twitch_api_user.create_twitch_user()

    @lazy
    def twitch_channel(self):
        channel_user = MockTwitchAPIUser.create()
        channel_user.create_twitch_user()
        return MockTwitchChannel(channel_user.username)

    @lazy
    def twitch_client(self):
        return twitch.client
