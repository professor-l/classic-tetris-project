from asgiref.sync import async_to_sync
from ..moderator import DiscordModerator

@DiscordModerator.register("543873755202584587")
class AllCapsModerator(DiscordModerator):
    def apply(self):
        if not self.message.isupper():
            async_to_sync(self.message.delete)()
