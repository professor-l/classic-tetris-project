from .command import Command, CommandException
from .. import discord
from datetime import datetime
from ..reportmatchmodule.processrequest import processRequest

@Command.register_discord_aj("reportmatch", "yadda yadaa", usage="reportmatch, yadda yadda")
class ReportMatch(Command):
    def execute(self, *args):        
        print (self.context.message.content)
        result = processRequest(self.context.message.content)
        self.send_message("```" + result + "```")