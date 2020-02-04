from asgiref.sync import async_to_sync

from ..env import env

class DiscordModerator:
    def __init__(self, message):
        self.message = message

    def dispatch(self):
        rule_class = DISCORD_MODERATION_MAP[str(self.message.channel.id)]
        rule = rule_class(self)
        rule.apply()

    @staticmethod
    def is_rule(message):
        return str(message.channel.id) in DISCORD_MODERATION_MAP.keys()




class AllCapsRule:
    def __init__(self, moderator):
        self.moderator = moderator
        self.message = self.moderator.message

    def apply(self):
        if any(ch.islower() for ch in self.message.content):
            async_to_sync(self.message.delete)()


DISCORD_MODERATION_MAP = {
    env("DISCORD_CAPS_CHANNEL"): AllCapsRule
}

