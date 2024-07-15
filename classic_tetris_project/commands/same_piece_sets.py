from .command import Command, CommandException
from ..util import Platform, DocSection

@Command.register()
class GetSamePiecesCommand(Command):
    """
    Outputs whether the specified user (or yourself) can use a version of Tetris
    with same piece sets.
    """
    aliases = ("sps", "samepieces", "samepiecesets")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "sps [username] (default username you)"
    section = DocSection.USER

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


@Command.register()
class SetSamePiecesCommand(Command):
    """
    Sets your ability to use same piece sets in gameplay. Options are
    y/yes/t/true and n/no/f/false.
    """
    aliases = ("setsps", "setsamepieces", "setsamepiecesets")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "setsps <y/n>"
    section = DocSection.USER

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
