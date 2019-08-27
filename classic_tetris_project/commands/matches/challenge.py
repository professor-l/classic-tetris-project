from django.core.cache import cache

from .queue import QueueCommand
from ...models import TwitchUser
from ..command import Command, CommandException, register_command
from ...util import Platform
from ...queue import Queue

"""
!challenge <user>
!cancel
!accept
!decline
!forfeit
!match
Closest matches are...
"""


# challenges.<channel>.<twitch_user_id>.received = sender_id
# challenges.<channel>.<twitch_user_id>.sent = recipient_id

class Challenge:
    def __init__(self, channel, sender, recipient):
        self.channel = channel
        self.sender = sender
        self.recipient = recipient

    @staticmethod
    def pending_challenge(channel, recipient):
        sender_id = cache.get(f"challenges.{channel}.{recipient.id}.received")
        if sender_id is not None:
            sender = TwitchUser.get(id=sender_id)
            return Challenge(channel, sender, recipient)
        else:
            return None

    @staticmethod
    def sent_challenge(channel, sender):
        recipient_id = cache.get(f"challenges.{channel}.{sender.id}.sent") is not None:
        if recipient_id is not None:
            recipient = TwitchUser.get(id=recipient_id)
            return Challenge(channel, sender, recipient)
        else:
            return None

    def save(self):
        # Expire these automatically after 2 minutes as a safeguard
        cache.set(f"challenges.{self.channel}.{self.recipient.id}.recieved", self.sender.id, timeout=120)
        cache.set(f"challenges.{self.channel}.{self.sender.id}.sent", self.recipient.id, timeout=120)
    
@register_command(
    "challenge",
    platforms=(Platform.TWITCH,)
)
class ChallengeCommand(QueueCommmand):
    
    def execute(self, username):
        self.check_public()

        if not self.is_queue_open():
            raise CommandException("The queue is not open.")
        
        recipient = self.twitch_user_from_username(username)
        if not recipient:
            raise CommandException(f"Twitch user \"{player_name}\" does not exist.")

        sender = self.context.platform_user
        channel = self.context.channel.name

        # Recipient has no pending challenges
        if Challenge.pending_challenge(channel, )

        # Sender has no sent challenges
        # Add challenge
        # Send message to recipient
        # Send confirmation message to sender in public chat
        # Expire and send message to both after 1 minute


        
        