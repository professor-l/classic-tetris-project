import time
import uuid
from threading import Thread
from django.core.cache import cache

from .queue import QueueCommand
from ...models import TwitchUser
from ..command import Command, CommandException, register_command
from ...util import Platform

"""
!challenge <user>
!cancel
!accept
!decline
!forfeit
!match
Closest matches are...
"""

CHALLENGE_TIMEOUT = 60

# challenges.<channel>.<twitch_user_id>.received = sender_id
# challenges.<channel>.<twitch_user_id>.sent = recipient_id

class Challenge:
    def __init__(self, channel, sender, recipient):
        self.channel = channel
        self.sender = sender
        self.recipient = recipient
        self.uuid = uuid.uuid4().hex

    @staticmethod
    def pending_challenge(recipient):
        return cache.get(f"challenges.{recipient.id}.received")

    @staticmethod
    def sent_challenge(sender):
        return cache.get(f"challenges.{sender.id}.sent")

    def save(self):
        # Expire these automatically after 2 minutes as a safeguard
        cache.set(f"challenges.{self.recipient.id}.received", self, timeout=120)
        cache.set(f"challenges.{self.sender.id}.sent", self, timeout=120)

    def expire(self):
        cache.delete(f"challenges.{self.recipient.id}.received")
        cache.delete(f"challenges.{self.sender.id}.sent")

    def __eq__(self, challenge):
        return self.uuid == challenge.uuid


@register_command(
    "challenge",
    platforms=(Platform.TWITCH,)
)
class ChallengeCommand(QueueCommand):
    usage = "challenge <user>"

    def execute(self, username):
        self.check_public()

        if not self.is_queue_open():
            raise CommandException("The queue is not open.")

        recipient = self.twitch_user_from_username(username)
        if not recipient:
            raise CommandException(f"Twitch user \"{player_name}\" does not exist.")

        sender = self.context.platform_user
        channel_name = self.context.channel.name

        # Check that recipient has no pending challenges

        if Challenge.pending_challenge(channel_name, recipient):
            raise CommandException(f"{username} already has a pending challenge.")

        # Check that sender has no pending challenges
        sent_challenge = Challenge.sent_challenge(channel_name, sender)
        if sent_challenge:
            raise CommandException("You have already challenged {sent_challenge.recipient.username}.")

        # Add challenge
        challenge = Challenge(channel_name, sender, recipient)
        challenge.save()

        # Send message to recipient
        recipient.send_message(f"{sender.username} has challenged you to a match on twitch.tv/{channel_name}! You have 60 seconds to !accept or !decline.")

        # Send confirmation message to sender in public chat
        self.send_message(f"{sender.user_tag}: Your challenge to {recipient.username} has been sent.")

        # Expire and send message to both after 1 minute
        # In the future, we may want to schedule this with Celery
        def send_delayed_expiration_message(challenge):
            time.sleep(CHALLENGE_TIMEOUT)
            existing_challenge = Challenge.pending_challenge(challenge.channel, challenge.recipient)
            if challenge == existing_challenge:
                sender.send_message(f"Your challenge to {challenge.recipient.username} has expired.")
                recipient.send_message(f"The challenge from {challenge.sender.username} has expired.")
                challenge.expire()

        expire_thread = Thread(target=send_delayed_expiration_message, args=(challenge,))
        expire_thread.start()


@register_command(
    "accept",
    (Platform.TWITCH,)
)
class AcceptChallengeCommand(QueueCommand):
    usage = "accept"

    def execute(self):

        # Check this is in a whisper
        self.check_private()

        # Check that the challenge exists
        Challenge.pending_challenge(self.con)
        # Check that the queue is open
        # Add the match to the queue
        # ???
