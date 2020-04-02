from .command import Command, CommandException
from .. import discord
from datetime import datetime
try:
    from ..reportmatchmodule.processrequest import (
        processRequest,
        updateChannel,
        setupChannel,
        checkChannelPeon
    )
    REPORT_MATCH_LOADED = True
except ModuleNotFoundError:
    REPORT_MATCH_LOADED = False


@Command.register_discord("reportmatch", usage="reportmatch, yadda yadda")
class ReportMatch(Command):
    def execute(self, *args):
        if REPORT_MATCH_LOADED:
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
        self.send_message("```" + result + "```")
        if league is not None:
            self.executeUpdate(league)

    # :redheart: setup cc
    def executeSetup(self, *args):
        league = args[0][1]
        setupChannel(self.context, league)

    def executeUpdate(self, league):
        print("Updating the channel image etc.")
        updateChannel(self.context, league)
