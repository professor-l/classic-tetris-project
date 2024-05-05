from .command import Command, CommandException

@Command.register("setpronouns", "setpronoun", usage="setpronoun <he/she/they>")
class SetPronounCommand(Command):
    def execute(self, pronoun):
        pronouns = ["he", "she", "they"]
        accept = [
            ["he", "him", "his", "he/him", "he/him/his"],
            ["she", "her", "hers", "she/her", "she/her/hers"],
            ["they", "them", "theirs", "they/them", "they/them/theirs"],
            ["it", "its", "it/its"],
            ["xe", "xem", "xir", "xe/xem", "xe/xem/xir"],
            ["none"]
        ]

        for i, p in enumerate(pronouns):
            if pronoun in accept[i]:
                if self.context.user.set_pronouns(p):
                    self.send_message("Your pronouns have been set to {np}!".format(
                        np=self.context.user.get_pronouns_display() or "none"
                    ))
                else:
                    raise CommandException("Error setting pronouns :(")
                return

        raise CommandException("Invalid pronoun option. Choose one of: he, she, they, it, xe, none")

Command.register("pronouns", "pronoun", "getpronouns", "getpronoun", usage="pronouns <username>")
class GetPronounCommand(Command):
    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)
        user = platform_user.user if platform_user else None

        username = self.context.display_name(user)
        pronouns = user.get_pronouns_display() or "not set"
        self.send_message("{name}'s pronouns are {pronouns}", username, pronouns)
