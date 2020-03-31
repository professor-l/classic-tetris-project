from .command import Command, CommandException
from .. import discord
from datetime import datetime
from ..reportmatchmodule.processrequest import (
    processRequest,
    updateChannel,
    setupChannel,
    checkChannelPeon
)

@Command.register_discord("schedulematch", usage="schedulematch, yadda yadda")
class ScheduleMatch(Command):
    def execute(self, *args):      
        self.executePeon(args)

    def executePeon(self, *args):
        # only accept reports in the reporting channel
        if not checkChannelPeon(self.context):
            return
        league, result = processRequest(self.context.author.nick, self.context.message.content)
        self.send_message("```" + result + "```")
        if league is not None:
            self.executeUpdate(league)

    def executeUpdate(self, league):
        updateChannel(self.context, league)
