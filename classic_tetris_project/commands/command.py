import logging
import re
import traceback
from inspect import signature
from discord import ChannelType
import django.db
from abc import ABC

from .. import discord, twitch
from ..util import Platform
from ..models.users import DiscordUser, TwitchUser
from ..env import env

RE_DISCORD_MENTION = re.compile(r"^<@!?(\d+)>$")
RE_DISCORD_TAG = re.compile(r"^@?((?P<username>[^@#:]+)#(?P<discriminator>\d+))$")
RE_TWITCH_USERNAME = re.compile(r"^@?(\w+)$")

class CommandException(Exception):
    def __init__(self, message=None, send_usage=False):
        self.message = message
        self.send_usage = send_usage

class Command(ABC):
    def __init__(self, context):
        self.context = context
        self.args = context.args

    def check_support_and_execute(self):
        if self.context.platform in self.supported_platforms:
            try:
                min_args, max_args = self.arity
                num_args = len(self.args)
                if num_args < min_args or (max_args is not None and num_args > max_args):
                    raise CommandException(send_usage=True)
                else:
                    # Close expired database conections before and after each command to avoid
                    # timeouts. This emulates Django's built-in behavior of closing connections
                    # before and after each web request.
                    django.db.close_old_connections()
                    self.execute(*self.args)
            except CommandException as e:
                if e.message:
                    self.send_message(e.message)
                if e.send_usage:
                    self.send_usage()
            except Exception as e:
                self.send_message("Internal error :(")
                self.context.logger.exception("Internal error :(")
            finally:
                django.db.close_old_connections()
        else:
            self.send_message("Command not supported on this platform.")

    def send_message(self, message):
        self.context.send_message(message)

    def send_usage(self):
        # Add `wrapper` if in Discord
        formatted = self.context.format_code("{prefix}{usage}".format(
            prefix=self.context.prefix,
            usage=self.usage
        ))
        self.send_message(f"Usage: {formatted}")

    def check_moderator(self):
        if self.context.platform == Platform.TWITCH:
            author = self.context.author
            channel = self.context.channel
            if not (author.is_moderator or
                    (channel.type == "channel" and self.context.author.username == channel.name)):
                raise CommandException()

        elif self.context.platform == Platform.DISCORD:
            guild = discord.get_guild()
            member = guild.get_member(self.context.author.id)
            role = guild.get_role(discord.moderator_role_id)

            if role not in member.roles:
                raise CommandException()

    def check_private(self):
        if self.context.platform == Platform.DISCORD:
            if self.context.channel.type != ChannelType.private:
                raise CommandException(
                    "This command only works in a direct message."
                )

        elif self.context.platform == Platform.TWITCH:
            if self.context.channel.type != "whisper":
                raise CommandException(
                    "This command only works in a direct message."
                )

    def check_public(self):
        if self.context.platform == Platform.DISCORD:
            if self.context.channel.type != ChannelType.text:
                raise CommandException(
                    "This command only works in a public channel."
                )

        elif self.context.platform == Platform.TWITCH:
            if self.context.channel.type != "channel":
                raise CommandException(
                    "This command only works in a public channel."
                )

    @property
    def usage(self):
        return self._usage_string

    @property
    def arity(self):
        min_args = 0
        max_args = 0
        sig = signature(self.execute)
        for param in sig.parameters.values():
            if param.kind == param.VAR_POSITIONAL:
                max_args = None
            else:
                if param.default == param.empty:
                    min_args += 1
                if max_args is not None:
                    max_args += 1
        return min_args, max_args

    def any_platform_user_from_username(self, username):
        try: 
            guild = self.context.guild if self.context.platform == platform.DISCORD else None 
            platform_user = Command.discord_user_from_username(username, guild)
        except CommandException:
            platform_user = None

        if platform_user is not None:
            return platform_user

        try:
            platform_user = Command.twitch_user_from_username(username)
        except CommmandException:
            platform_user = None

        if platform_user is not None:
            return platform_user

        # Explicitly return None if no user was found
        return None


    def platform_user_from_username(self, username):
        if self.context.platform == Platform.DISCORD:
            return Command.discord_user_from_username(username, self.context.guild)
        elif self.context.platform == Platform.TWITCH:
            return Command.twitch_user_from_username(username)

    @staticmethod
    def discord_user_from_username(username, guild=None):
        match_mention = RE_DISCORD_MENTION.match(username)
        match_tag = RE_DISCORD_TAG.match(username)

        if match_mention:
            discord_id = match_mention.group(1)
            try:
                return DiscordUser.objects.get(discord_id=discord_id)
            except DiscordUser.DoesNotExist:
                return None
        else:
            if guild is None:
                guild = discord.get_guild()

            member = None
            for user in guild.members:
                if user.display_name.casefold() == username.casefold():
                    member = user
                    break

            if member is not None:
                try:
                    return DiscordUser.objects.get(discord_id=member.id)
                except DiscordUser.DoesNotExist:
                    return None
            else:
                raise CommandException("Invalid username")

    @staticmethod
    def twitch_user_from_username(username):
        match = RE_TWITCH_USERNAME.match(username)

        if match:
            username = match.group(1)
            user = TwitchUser.from_username(username)
            if user and user.twitch_id == twitch.client.user_id:
                raise CommandException("I'm a bot, silly!")

            return user
        else:
            raise CommandException("Invalid username")

    @staticmethod
    def register(*aliases, usage, platforms=(Platform.DISCORD, Platform.TWITCH)):
        def _register_command(command):
            command.supported_platforms = platforms
            command._usage_string = usage
            for alias in aliases:
                COMMAND_MAP[alias] = command
            return command
        return _register_command

    @staticmethod
    def register_twitch(*args, **kwargs):
        return Command.register(*args, **kwargs, platforms=(Platform.TWITCH,))

    @staticmethod
    def register_discord(*args, **kwargs):
        return Command.register(*args, **kwargs, platforms=(Platform.DISCORD,))

    def execute(self):
        pass

class CustomTwitchCommand(Command):
    def __init__(self, context, command_object):
        super().__init__(context)
        self.supported_platforms = [Platform.TWITCH]

        self.output = command_object.output or command_object.alias_for.output

    def execute(self, *args):
        self.send_message(self.output)

COMMAND_MAP = {}
