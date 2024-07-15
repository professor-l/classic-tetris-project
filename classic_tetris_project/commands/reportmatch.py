from .command import Command, CommandException
from .. import discord
from ..models.users import User
from ..util import Platform, DocSection

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
import time

# not registering this since it probably shouldn't be used anymore
# @Command.register()
class ReportMatch(Command):
    """
    reports a match i guess (this command should not be used)
    """
    aliases = ("reportmatch",)
    supported_platforms = (Platform.DISCORD,)
    usage = "reportmatch [insert args here]"
    notes = ("Will be either deprecated or refactored",)
    section = DocSection.OTHER

    def execute(self, *args):
        if not REPORT_MATCH_LOADED:
            return
        if len(args) > 1 and args[0] == "setup":  # hackerman...
            self.check_moderator()
            self.execute_setup(args)
        else:
            self.execute_peon(args)

    def execute_peon(self, *args):
        # only accept reports in the reporting channel
        if not checkChannelPeon(self.context):
            return
        
        # preference for names. Nickname, display_name.
        name = (self.context.author.nick or 
               self.context.author.display_name or 
               str(self.context.author))
        
        league, result = processRequest(name, self.context.message.content)
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
        

    # :redheart: setup cc
    def execute_setup(self, *args):
        league = args[0][1]
        setupChannel(self.context, league, self.all_users())

    def execute_update(self, league):
        print("Updating the channel image etc.")
        updateChannel(self.context, league, self.all_users())

    def all_users(self):
        query = list(User.objects.exclude(twitch_user=None).exclude(discord_user=None).all())
        result = {}
        for user in query:
            try:
                result[user.twitch_user.username] = user.discord_user.display_name()
            except: #pokemon
                pass
        return result
