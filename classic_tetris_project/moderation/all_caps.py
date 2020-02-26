from .rule import DiscordRule

class AllCapsRule(DiscordRule):

    def apply(self):
        if any(ch.islower() for ch in self.message.content):
            self.delete_message()

