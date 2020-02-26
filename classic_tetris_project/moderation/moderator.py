from ..env import env
from ..models.users import DiscordUser
from ..util import memoize

# Explicitly importing all rules
# We want to be very, very sure we WANT a rule before we add it
from .all_caps import AllCapsRule

class DiscordModerator:
    def __init__(self, message):
        self.message = message

    def dispatch(self):
        rule_class = DISCORD_MODERATION_MAP[str(self.message.channel.id)]
        rule = rule_class(self)
        rule.apply()

    @property
    @memoize
    def user(self):
        return DiscordUser.fetch_by_discord_id(self.message.author.id)

    @staticmethod
    def is_rule(message):
        return str(message.channel.id) in DISCORD_MODERATION_MAP.keys()


DISCORD_MODERATION_MAP = {
    env("DISCORD_CAPS_CHANNEL"): AllCapsRule
}

