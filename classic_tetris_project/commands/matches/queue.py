

from .command import Command, CommandException, register_command
from ..util import Platform
from ..queue import Queue

"""
!open
!close
!addmatch <player1> <player2>
!removematch <id>
!clear
!queue !q !matches

!endmatch
!winner

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
    platform=(Platform.TWITCH,)
)
class OpenQueueCommand(Command):
    usage = "open"

    def execute(self):
        self.check_moderator()
        
        channel_name = self.context.channel.name
        if Queue.get(channel_name):
            raise CommandException("The queue has already been opened.")
        else:
            Queue(channel_name).save()
            self.send_message("The queue is now open!")


@register_command(
    "close", "closequeue",
    platform=(Platform.TWITCH,)
)
class CloseQueueCommand(Command):
    usage = "close"

    def execute(self):
        self.check_moderator()

        channel_name = self.context.channel.name
        queue = Queue.get(channel_name)
        if queue is None:
            raise CommandException("The queue isn't open!")
        else:
            queue.open = False
        
    

"""
@register_command(
    "addmatch", 
    platforms=(Platform.TWITCH,)
)
class AddMatchCommand(Command):
    usage = "addmatch <player 1> <player 2>"
    def execute(self, player1, player2):
        if self.context.channel.type != "channel":
            raise CommandException("Command must be run in a public channel.")
        queue = Queue.get_queue(self.context.channel.name)
"""
