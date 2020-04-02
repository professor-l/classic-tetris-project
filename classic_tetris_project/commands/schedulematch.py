from .command import Command, CommandException
from .. import discord
import time
from ..models.users import TwitchUser
from ..reportmatchmodule.processrequest import (
    processRequest,
    updateChannel,
    setupChannel,
    checkChannelPeon
)

@Command.register_discord("schedulematch", usage="schedulematch, yadda yadda")
class ScheduleMatch(Command):
    def execute(self, *args):      
        self.execute_peon(args)

    def execute_peon(self, *args):
        # only accept reports in the reporting channel
        if not checkChannelPeon(self.context):
            return
        league, result = processRequest(self.context.author.nick, self.context.message.content)
        temp_message = self.send_message("```" + result + "```")
        if league is not None:
            self.context.add_reaction(self.context.message, '🇦')
            self.context.add_reaction(self.context.message, '🇮')
            self.execute_update(league)
            self.context.delete_message(temp_message)           
        else:
            self.context.add_reaction(self.context.message, '🚫')
            time.sleep(10)

            items = ["5⃣","4⃣", "3⃣", "2⃣", "1⃣"]
            for i in range(5):
                self.context.add_reaction(temp_message, items[i])
                time.sleep(1)

            self.context.delete_message(temp_message)

    def execute_update(self, league):
        updateChannel(self.context, league, self.all_users())
   
    def all_users(self):
        query = list(User.objects.exclude(twitch_user=None).exclude(discord_user=None).all())
        result = {}
        for user in query:
            result[user.twitch_user.username] = user.discord_user.username
        return result