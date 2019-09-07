import re
from asgiref.sync import async_to_sync
from .command import COMMAND_MAP
from ..util import Platform, memoize
from ..models.users import DiscordUser, TwitchUser

class CommandContext:
    def __init__(self, content):
        self.content = content
        try:
            self.args_string = content[(content.index(" ") + 1):]
        except ValueError:
            self.args_string = ""

        trimmed = re.sub(r"\s+", " ", content).strip()
        tokens = trimmed[len(self.prefix):].split(" ")
        self.command_name = tokens[0].lower()
        self.args = tokens[1:]

    def dispatch(self):
        command_class = COMMAND_MAP.get(self.command_name)
        if command_class:
            command = command_class(self)
            command.check_support_and_execute()
        else:
            # Not a valid command
            pass

    @classmethod
    def is_command(cls, message):
        return message.startswith(cls.prefix)

    @property
    def user(self):
        return self.platform_user.user

    def format_code(self, message):
        return message



class DiscordCommandContext(CommandContext):
    platform = Platform.DISCORD
    prefix = "!"
    def __init__(self, message):
        super().__init__(message.content)

        self.message = message
        self.channel = message.channel
        self.author = message.author

    def send_message(self, message):
        async_to_sync(self.channel.send)(message)

    @property
    def user_tag(self):
        return f"<@{self.author.id}>"

    @property
    @memoize
    def platform_user(self):
        return DiscordUser.fetch_by_discord_id(self.author.id)

    def format_code(self, message):
        return f"`{message}`"



class TwitchCommandContext(CommandContext):
    platform = Platform.TWITCH
    prefix = "!"

    def __init__(self, message):
        super().__init__(message.content)

        self.message = message
        self.channel = message.channel
        self.author = message.author

    def send_message(self, message):
        self.channel.send_message(message)

    @property
    def user_tag(self):
        return f"@{self.author.username}"

    @property
    @memoize
    def platform_user(self):
        twitch_user = TwitchUser.fetch_by_twitch_id(self.author.id)
        twitch_user.update_username(twitch_user.user_obj.username)
        return twitch_user
