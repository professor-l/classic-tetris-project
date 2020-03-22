from .command import Command, CommandException
from .. import discord
from datetime import datetime
from ..reportmatchmodule.processrequest import processRequest, updateChannel, setupChannel

@Command.register_discord_aj("reportmatch", "yadda yadaa", usage="reportmatch, yadda yadda")
class ReportMatch(Command):
    def execute(self, *args):
        if len(args) > 1 and args[0] == "setup": #hackerman...
            self.executeSetup(args)
        else:
            self.executePeon(args)

    def executePeon(self, *args):
        print (self.context.message.content)
        league, result = processRequest(self.context.message.content)
        self.send_message("```" + result + "```")
        if league is not None:
            self.executeUpdate(league)

    # :redheart: setup cc
    def executeSetup(self, *args):        
        league = args[0][1]
        setupChannel(self.context, league)
        
    def executeUpdate(self, league):
        print ("Updating the channel image etc.")
        updateChannel(self.context, league)