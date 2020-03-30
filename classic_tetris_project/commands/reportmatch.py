from .command import Command, CommandException
from .. import discord

from ..reportmatchmodule.processrequest import (
    processRequest,
    updateChannel,
    setupChannel,
    checkChannelPeon
)
import time

@Command.register_discord("reportmatch", usage="reportmatch, yadda yadda")
class ReportMatch(Command):
    def execute(self, *args):
        if len(args) > 1 and args[0] == "setup":  # hackerman...
            self.check_moderator()
            self.executeSetup(args)
        else:
            self.executePeon(args)

    def executePeon(self, *args):
        # only accept reports in the reporting channel
        if not checkChannelPeon(self.context):
            return
        league, result = processRequest(self.context.author.nick, self.context.message.content)
        tempMessage = self.send_message("```" + result + "```")
        print(tempMessage)
        if league is not None:
            self.context.add_reaction(self.context.message, '🇦')
            self.context.add_reaction(self.context.message, '🇮')
            self.executeUpdate(league)
            self.context.delete_message(tempMessage)
        else:
            self.context.add_reaction(self.context.message, '🚫')
            time.sleep(10)

            items = ["5⃣","4⃣", "3⃣", "2⃣", "1⃣"]
            for i in range(5):
                self.context.add_reaction(tempMessage, items[i])
                time.sleep(1)

            self.context.delete_message(tempMessage)
        

    # :redheart: setup cc
    def executeSetup(self, *args):
        league = args[0][1]
        setupChannel(self.context, league)

    def executeUpdate(self, league):
        print("Updating the channel image etc.")
        updateChannel(self.context, league)
