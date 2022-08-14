from .command import Command, CommandException

@Command.register("link", "linkaccount", usage="link")
class LinkCommand(Command):
    def execute(self, *args):
        self.send_message("To link your Twitch or Discord account, head to our website and click 'Login' at the top right: https://go.ctm.gg.  Once there, you can view and edit your profile.")
