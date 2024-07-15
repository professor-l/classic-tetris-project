import uuid
from django.core.cache import cache

from .queue import QueueCommand
from ..command import Command, CommandException
from ...queue import Queue
from ... import twitch
from ...util import Platform, DocSection

"""
!challenge <user>
!cancel
!accept
!decline
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
        print(f"setting challenges.{self.recipient.id}.received")
        cache.set(f"challenges.{self.recipient.id}.received", self, timeout=CHALLENGE_TIMEOUT)
        cache.set(f"challenges.{self.sender.id}.sent", self, timeout=CHALLENGE_TIMEOUT)

    def remove(self):
        cache.delete(f"challenges.{self.recipient.id}.received")
        cache.delete(f"challenges.{self.sender.id}.sent")

    def __eq__(self, challenge):
        return isinstance(challenge, Challenge) and self.uuid == challenge.uuid


@Command.register()
class ChallengeCommand(QueueCommand):
    """
    Challenges the specified user to a match. Only one challenge can be pending
    to a user at a time, and each user may only issue one challenge at a time.
    """
    aliases = ("challenge",)
    supported_platforms = (Platform.TWITCH,)
    usage = "challenge <user>"
    notes = ("Must be run in a public channel",)
    section = DocSection.QUEUE

    def execute(self, username):
        self.check_public()

        if not self.is_queue_open():
            raise CommandException("The queue is not open.")

        recipient = self.twitch_user_from_username(username, existing_only=False)
        if not recipient:
            raise CommandException(f"Twitch user \"{username}\" does not exist.")

        sender = self.context.platform_user
        if recipient == sender:
            raise CommandException("You can't challenge yourself, silly!")
        channel_name = self.context.channel.name

        # Check that recipient has no pending challenges
        # TODO: We may want to allow multiple challenges in the future, but
        # allow users to choose which to accept
        if Challenge.pending_challenge(recipient):
            raise CommandException(f"{username} already has a pending challenge.")

        # Check that sender has no pending challenges
        sent_challenge = Challenge.sent_challenge(sender)
        if sent_challenge:
            raise CommandException(f"You have already challenged {sent_challenge.recipient.username}.")

        # Add challenge
        challenge = Challenge(channel_name, sender, recipient)
        challenge.save()

        # Send public message announcing challenge
        self.send_message(f"{recipient.user_tag} : {sender.username} has challenged you to a match on twitch.tv/{channel_name}! You have 60 seconds to !accept or !decline.")


@Command.register()
class AcceptChallengeCommand(Command):
    """
    Accepts the pending challenge to you, if there is one, and adds that match
    to the queue.
    """
    aliases = ("accept",)
    supported_platforms = (Platform.TWITCH,)
    usage = "accept"
    notes = ("Must be run in a private message",)
    section = DocSection.QUEUE

    def execute(self):
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


@Command.register()
class DeclineChallengeCommand(Command):
    """
    Declines the pending challenge to you, if there is one.
    """
    aliases = ("decline",)
    supported_platforms = (Platform.TWITCH,)
    usage = "decline"
    notes = ("Must be run in a private message",)
    section = DocSection.QUEUE

    def execute(self):
        challenge = Challenge.pending_challenge(self.context.platform_user)
        if not challenge:
            raise CommandException("You have no pending challenge.")

        challenge.remove()
        self.send_message(f"{challenge.recipient.username} has declined {challenge.sender.username} 's challenge.")

@Command.register()
class CancelChallengeCommand(Command):
    """
    Cancels your pending challenge to someone else, if you have issued one.
    """
    aliases = ("cancel",)
    supported_platforms = (Platform.TWITCH,)
    usage = "cancel"
    notes = ("Must be run in a public channel",)
    section = DocSection.QUEUE

    def execute(self):
        self.check_public()

        challenge = Challenge.sent_challenge(self.context.platform_user)
        if not challenge:
            raise CommandException("You have not challenged anyone.")

        challenge.remove()
        self.send_message("The challenge from {sender} to {recipient} has been cancelled.".format(
            sender=challenge.sender.username,
            recipient=challenge.recipient.username
        ))
