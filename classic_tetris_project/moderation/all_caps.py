from .rule import DiscordRule
import time

class AllCapsRule(DiscordRule):

    def apply(self):
        if any(ch.islower() for ch in self.message.content):
            time.sleep(0.5) #wait half a second, due to clientside bug.
            self.delete_message()

