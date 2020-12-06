import itertools
import lxml.html
import re
from contextlib import contextmanager
from django.test import TestCase as DjangoTestCase
from django.test import override_settings
from django.core.cache import cache
from unittest.mock import patch

from classic_tetris_project.commands.command_context import *
from classic_tetris_project.models import *
from classic_tetris_project.util.memo import memoize, lazy
from .factories import *
from .discord import *
from .twitch import *
from classic_tetris_project import discord, twitch



patch.object(twitch.APIClient, "_request", side_effect=Exception("twitch API called")).start()
patch.object(discord.APIClient, "_request", side_effect=Exception("discord API called")).start()

@contextmanager
def describe(description):
    """
    noop, just used to provide structure to test classes
    """
    yield

# Based loosely on https://github.com/johnpaulett/django-with-asserts
class AssertHTMLMixin:
    def assertHTML(self, response, selector, text=None):
        html = lxml.html.fromstring(response.content)
        elements = html.cssselect(selector)
        if not elements:
            raise AssertionError(f"No element found matching '{selector}'")
        if text:
            for element in elements:
                if element.text.strip() == text:
                    return
            raise AssertionError(f"No element found matching '{selector}' with text '{text}'")

@override_settings(
    TESTING=True,
    DEBUG=True,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    },
)
class TestCase(DjangoTestCase, AssertHTMLMixin):
    """
    Augment Django's TestCase class with some of our own convenience methods
    """

    def setUp(self):
        pass

    def tearDown(self):
        cache.clear()

    def setUp(self):
        self._patches = self.patches()

        for _patch in self._patches:
            _patch.start()

    def patches(self):
        return [
            patch("classic_tetris_project.twitch.client", MockTwitchClient()),
        ]

    def tearDown(self):
        for patch in self._patches:
            patch.stop()
        cache.clear()

    @lazy
    def current_user(self):
        return UserFactory()

    @lazy
    def current_website_user(self):
        return WebsiteUser.fetch_by_user(self.current_user)

    @lazy
    def current_auth_user(self):
        return self.current_website_user.auth_user

    def sign_in(self):
        self.client.force_login(self.current_auth_user)

    def get(self, *args, **kwargs):
        return self.client.get(self.url, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(self.url, *args, **kwargs)


class CommandTestCase(TestCase):
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

    def assertDiscord(self, command, expected_messages):
        self.send_discord(command, flush=False)
        actual_messages = self.discord_channel.poll()
        self._assertMessages(actual_messages, expected_messages)

    def assertTwitch(self, command, expected_messages):
        self.send_twitch(command, flush=False)
        actual_messages = self.twitch_channel.poll()
        self._assertMessages(actual_messages, expected_messages)

    def _assertMessages(self, actual_messages, expected_messages):
        for actual, expected in itertools.zip_longest(actual_messages, expected_messages,
                                                      fillvalue=""):
            if isinstance(expected, str):
                self.assertEqual(actual, expected)
            elif isinstance(expected, re.Pattern):
                self.assertRegex(actual, expected)
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
