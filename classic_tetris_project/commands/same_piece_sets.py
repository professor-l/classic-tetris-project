from .command import Command, CommandException
from ..util import Platform

@Command.register("samepieces", "samepiecesets", 
                  usage="samepieces [username] (default username you)")
class GetSamePiecesCommand(Command):
    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)

        if not platform_user or not platform_user.user:
            self.send_message("The specified user does not exist.")

        user = platform_user.user

        s = "CAN" if user.same_piece_sets else "CANNOT"
        if self.context.platform == Platform.DISCORD:
            s = "**" + s + "**"

        self.send_message("{user_tag} {ability} use same piece sets.".format(
            user_tag = platform_user.user_tag,
            ability = s
        ))


@Command.register("setsamepieces", "setsamepiecesets", 
                  usage="setsamepieces [y/n]")
class SetSamePiecesCommand(Command):
    def execute(self, value):
        print("EXECUTING")
        if self.context.user.set_same_piece_sets(value):
            ability = "Yes" if self.context.user.same_piece_sets else "No"
            self.send_message(
                "{user_tag} - Your ability to use same piece sets has been set to: {ability}.".format(
                    user_tag=self.context.platform_user.user_tag,
                    ability="\"" + ability + "\""
            ))

        else:
            self.send_message("Invalid option - must be y/n.")
