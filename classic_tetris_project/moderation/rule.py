from asgiref.sync import async_to_sync

class DiscordRule:
    def __init__(self, moderator):
        self.moderator = moderator
        self.message = self.moderator.message
    
    def delete_message(self):
        async_to_sync(self.message.delete)()

    def notify_user(self, message):
        self.moderator.user.send_message(message)
