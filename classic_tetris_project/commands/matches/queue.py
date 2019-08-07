from ..command import Command, CommandException, register_command
from ...util import Platform
from ...queue import Queue

"""
queue.py:
    !open
    !close
    !addmatch <player1> <player2>
    !removematch <id>
    !clear
    !queue !q !matches
    !endmatch
    !winner

challenge.py
    !challenge
    !cancel
    !accept
    !decline
    !forfeit
    !match
    Closest matches are...

"""

@register_command(
    "open", "openqueue",
    platforms=(Platform.TWITCH,)
)
class OpenQueueCommand(Command):
    usage = "open"

    def execute(self):
        self.check_public()
        self.check_moderator()

        channel_name = self.context.channel.name
        queue = Queue.get(channel_name)
        if queue and queue.is_open:
            raise CommandException("The queue has already been opened.")
        else:
            if queue:
                queue.open()
                self.send_message("The queue has been repoened!")
            else:
                queue = Queue(channel_name)
                queue.open()
                self.send_message("The queue is now open!")


@register_command(
    "close", "closequeue",
    platforms=(Platform.TWITCH,)
)
class CloseQueueCommand(Command):
    usage = "close"

    def execute(self):
        self.check_public()
        self.check_moderator()

        channel_name = self.context.channel.name
        queue = Queue.get(channel_name)
        if queue is None or not queue.is_open:
            raise CommandException("The queue isn't open!")
        else:
            queue.close()
            self.send_message("The queue has been closed.")   


@register_command(
    "addmatch", 
    platforms=(Platform.TWITCH,)
)
class AddMatchCommand(Command):
    usage = "addmatch <player 1> <player 2>"

    def execute(self, player1, player2):
        self.check_public()
        self.check_moderator()

        channel_name = self.context.channel.name
        queue = Queue.get(channel_name)
        if queue is None or not queue.is_open:
            raise CommandException("The queue is not open.")
        else:
            twitch_user1 = Command.twitch_user_from_username(player1)
            twitch_user2 = Command.twitch_user_from_username(player2)

            if twitch_user1 is None:
                raise CommandException(f"The twitch user \"{player1}\" does not exist.")
            if twitch_user2 is None:
                raise CommandException(f"The twitch user \"{player2}\" does not exist.")
                
            queue.add_match(twitch_user1, twitch_user2)
            self.send_message(f"A match has been added between {twitch_user1.user_tag} and {twitch_user2.user_tag}!")
