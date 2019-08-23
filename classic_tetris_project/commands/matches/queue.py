from django.core.exceptions import ObjectDoesNotExist

from ..command import Command, CommandException, register_command
from ...util import Platform
from ...queue import Queue
from ...util import memoize

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



class QueueCommand(Command):
    @property
    @memoize
    def queue(self):
        return Queue.get(self.context.channel.name)

    def is_queue_open(self):
        return self.queue and self.queue.is_open()

    def stringify_queue(self, queue):
        s = []
        for i, match in enumerate(queue.matches):
            try:
                s.append("[{index}]: {player1} vs. {player2}".format(
                    index=i+1,
                    player1=match.player1.twitch_user.username,
                    player2=match.player2.twitch_user.username
                ))
            except ObjectDoesNotExist:
                pass

        return " ".join(s) or "No current queue."


@register_command(
    "open", "openqueue",
    platforms=(Platform.TWITCH,)
)
class OpenQueueCommand(QueueCommand):
    usage = "open"

    def execute(self):
        self.check_public()
        self.check_moderator()

        if self.is_queue_open():
            raise CommandException("The queue has already been opened.")
        else:
            if self.queue:
                self.queue.open()
                self.send_message("The queue has been repoened!")
            else:
                Queue(self.context.channel.name).open()
                self.send_message("The queue is now open!")


@register_command(
    "close", "closequeue",
    platforms=(Platform.TWITCH,)
)
class CloseQueueCommand(QueueCommand):
    usage = "close"

    def execute(self):
        self.check_public()
        self.check_moderator()

        if not self.is_queue_open():
            raise CommandException("The queue isn't open!")
        else:
            self.queue.close()
            self.send_message("The queue has been closed.")   


@register_command(
    "queue", "q", "matches",
    platforms=(Platform.TWITCH,)
)
class ShowQueueCommand(QueueCommand):
    usage = "queue"

    def execute(self):
        self.check_public()
        self.send_message(self.stringify_queue(self.queue))


@register_command(
    "addmatch", 
    platforms=(Platform.TWITCH,)
)
class AddMatchCommand(QueueCommand):
    usage = "addmatch <player 1> <player 2>"

    def execute(self, player1, player2):
        self.check_public()
        self.check_moderator()

        if not self.is_queue_open():
            raise CommandException("The queue is not open.")
        else:
            twitch_user1 = Command.twitch_user_from_username(player1)
            twitch_user2 = Command.twitch_user_from_username(player2)

            if twitch_user1 is None:
                raise CommandException(f"The twitch user \"{player1}\" does not exist.")
            if twitch_user2 is None:
                raise CommandException(f"The twitch user \"{player2}\" does not exist.")
                
            self.queue.add_match(twitch_user1.user, twitch_user2.user)
            self.send_message(f"A match has been added between {twitch_user1.user_tag} and {twitch_user2.user_tag}!")
            

@register_command(
    "removematch",
    platforms=(Platform.TWITCH,)
)
class RemoveMatchCommand(QueueCommand):
    usage = "removematch <index>"

    def execute(self, index):
        self.check_public()
        self.check_moderator()

        try:
            index = int(index)
        except ValueError:
            raise CommandException("Invalid index.")
            
        if index < 1 or index > len(self.queue.matches):
            raise CommandException("No match at specified index.")
        else:
            self.queue.remove_match(index - 1)
            self.send_message("Match removed! New queue: {queue}".format(
                queue=self.stringify_queue(self.queue)
            ))


@register_command(
    "clear", "clearqueue",
    platforms=(Platform.TWITCH,)
)
class ClearQueueCommand(QueueCommand):
    usage = "clear yesimsure"
    
    def execute(self, comfirm):
        self.check_public()
        self.check_moderator()
        
        if comfirm == "yesimsure":
            self.queue.clear()
            self.send_message("The queue has been cleared.")

        else:
            self.send_usage()


@register_command(
    "winner", "declarewinner",
    platforms=(Platform.TWITCH,)
)
class DeclareWinnerCommand(QueueCommand):
    usage = "winner <player> [losing score]"

    def execute(self, player_name, losing_score=None):
        self.check_public()
        self.check_moderator()

        if self.queue.is_empty():
            raise CommandException("There is no current match.")
        try:
            losing_score = int(losing_score)
        except ValueError:
            raise CommandException("Invalid losing score.")
        
        if losing_score < 0 or losing_score > 1400000:
            raise CommandException("Invalid losing score.")

        twitch_user = self.twitch_user_from_username(player_name)
        if not twitch_user:
            self.send_message(f"Twitch user \"{player_name}\" does not exist.")

        
        user = Command.twitch_user_from_username(player_name).user
        try:
            self.queue.declare_winner(user, int(losing_score))
        except ValueError:
            raise CommandException(f"player \"{twitch_user.username}\" is not in the current match.")
            
        current_match = self.queue.current_match
        current_winner = current_match.get_current_winner()

        beginning_string = f"{twitch_user.username} has won a game!"
        middle_string = "The score is now {score1}-{score2}.".format(
            score1=current_match.wins1,
            score2=current_match.wins2
        )
        if current_winner:
            end_string = f"{current_winner.twitch_user.username} is ahead!"
        else:
            end_string = "It's all tied up!"
        
        strings = [beginning_string, middle_string, end_string]
        self.send_message(" ".join(strings))
