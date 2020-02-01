class ModeratorContext:
    pass

class DiscordModeratorContext:
    def __init__(self, message):
        self.message = message

    def dispatch(self):
        rule_class = DISCORD_MODERATION_MAP[self.message.channel.id]
        rule = rule_class(self)
        rule.apply()

    @staticmethod
    def is_rule(message):
        print(len(list(DISCORD_MODERATION_MAP.keys())))
        return message.channel.id in DISCORD_MODERATION_MAP.keys()



class Moderator:
    pass

class DiscordModerator(Moderator):
    def __init__(self, context):
        self.message = context.message

    @staticmethod
    def register(channel_id):
        def _register_rule(rule):
            DISCORD_MODERATION_MAP[channel_id] = rule
            return rule
        return _register_rule


DISCORD_MODERATION_MAP = {}
