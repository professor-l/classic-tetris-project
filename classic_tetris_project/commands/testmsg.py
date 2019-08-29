from .command import Command

@Command.register("testmsg",
                  usage="testmsg")
class TestMessageCommand(Command):
    def execute(self, *username):
        username = " ".join(username)

        platform_user = self.platform_user_from_username(username)
        platform_user.send_message("Test!")
