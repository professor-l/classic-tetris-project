import time
import uuid
from threading import Thread
from django.core.cache import cache

from .queue import QueueCommand
from ...models import TwitchUser
from ..command import Command, CommandException, register_command
from ...util import Platform
from ...queue import Queue
from ... import twitch

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

    def remove(self):
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
        # TODO: We may want to allow multiple challenges in the future, but
        # allow users to choose which to accept
        if Challenge.pending_challenge(recipient):
            raise CommandException(f"{username} already has a pending challenge.")

        # Check that sender has no pending challenges
        sent_challenge = Challenge.sent_challenge(sender)
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
            existing_challenge = Challenge.pending_challenge(challenge.recipient)
            if challenge == existing_challenge:
                sender.send_message(f"Your challenge to {challenge.recipient.username} has expired.")
                recipient.send_message(f"The challenge from {challenge.sender.username} has expired.")
                challenge.remove()

        expire_thread = Thread(target=send_delayed_expiration_message, args=(challenge,))
        expire_thread.start()


@register_command(
    "accept",
    (Platform.TWITCH,)
)
class AcceptChallengeCommand(Command):
    usage = "accept"

    def execute(self):

        # Check this is in a whisper
        self.check_private()

        # Check that the challenge exists
        challenge = Challenge.pending_challenge(self.context.platform_user)
        if not challenge:
            raise CommandException("You have no pending challenge.")

        # Check that the queue is open
        queue = Queue.get(challenge.channel)
        if not (queue and queue.is_open()):
            raise CommandException("The queue is no longer open. :(")

        # Add the match to the queue
        queue.add_match(challenge.sender.user, challenge.recipient.user)
        # Remove the challenge
        challenge.remove()

        # Send public message
        channel = twitch.client.get_channel(challenge.channel)
        channel.send_message("{recipient} has accepted {sender}'s challenge! Match queued in spot {index}.".format(
            recipient=challenge.recipient.user_tag,
            sender=challenge.sender.user_tag,
            index=len(queue)
        ))


@register_command(
    "decline",
    (Platform.TWITCH)
)
class DeclineChallengeCommand(Command):
    usage = "decline"

    def execute(self):
        self.check_private()

        challenge = Challenge.pending_challenge(self.context.platform_user)
        if not challenge:
            raise CommandException("You have no pending challenge.")

        challenge.remove()
        self.send_message(f"You have declined {challenge.sender.username}'s challenge.")
        challenge.sender.send_message(f"{challenge.recipient.username} has declined your challenge.")
