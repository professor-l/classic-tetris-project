from .command import Command, CommandException

@Command.register("setpronouns", "setpronoun", usage="setpronoun <he/she/they>")
class SetPronounCommand(Command):
    def execute(self, pronoun):
        pronouns = ["he", "she", "they"]
        accept = [
            ["he", "him", "his", "he/him", "he/him/his"],
            ["she", "her", "hers", "she/her", "she/her/hers"],
            ["they", "them", "theirs", "they/them", "they/them/theirs"]
        ]

        for i, p in enumerate(pronouns):
            if pronoun in accept[i]:
                if self.context.user.set_pronouns(p):
                    self.send_message("Your pronouns have been set to {np}!".format(
                        np=self.context.user.get_pronouns_display()
                    ))
                else:
                    raise CommandException("Error setting pronouns :(")
                return

        raise CommandException("Invalid pronoun option. Choose one of: he, she, they")

