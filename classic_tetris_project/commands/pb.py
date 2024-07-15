from .command import Command, CommandException
from ..util import Platform, DocSection

@Command.register()
class GetPBCommand(Command):
    """
    Prints a list of pbs for the specified user, or yourself if no argument is
    provided.
    """
    aliases = ("pb", "getpb")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "pb [username] (default username you)"
    section = DocSection.USER

    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string

        platform_user = (self.any_platform_user_from_username(username) if username
                         else self.context.platform_user)

        if not platform_user:
            raise CommandException("User has not set a PB.")

        user = platform_user.user
        name = self.context.display_name(platform_user)

        ntsc_pb = user.get_pb("ntsc")
        pal_pb = user.get_pb("pal")

        lvl_pbs = []
        for lvl in (19, 29):
            pb = user.get_pb("ntsc", lvl)
            if pb:
                lvl_pbs.append((lvl, pb))
        # TODO: this logic is weird but it's not worth fixing until pbs are
        # refactored correctly
        if ntsc_pb:
            ntsc_pb_text = "{pb:,}".format(pb=ntsc_pb)
            pb_strings = [f"{score:,} {lvl} start" for (lvl, score) in lvl_pbs]
            if len(pb_strings) > 0:
                extra_pb_string = ", ".join(pb_strings)
                ntsc_pb_text += f" ({extra_pb_string})"

        if pal_pb:
            pal_pb_text = "{pb:,}".format(pb=pal_pb)

        if ntsc_pb and pal_pb:
            self.send_message("{name} has an NTSC PB of {ntsc} and a PAL PB of {pal}.".format(
                name=name,
                ntsc=ntsc_pb_text,
                pal=pal_pb_text
            ))
        elif ntsc_pb:
            self.send_message("{name} has an NTSC PB of {ntsc}.".format(
                name=name,
                ntsc=ntsc_pb_text
            ))
        elif pal_pb:
            self.send_message("{name} has a PAL PB of {pb}.".format(
                name=name,
                pb=pal_pb_text
            ))
        else:
            self.send_message("User has not set a PB.")


@Command.register()
class SetPBCommand(Command):
    """
    Sets your personal best in either NTSC or PAL with the indicated starting
    level (defaults to 18).
    """
    aliases = ("setpb", "newpb")
    supported_platforms = (Platform.DISCORD, Platform.TWITCH)
    usage = "setpb <score> [type=NTSC] [level=18]"
    section = DocSection.USER

    def execute(self, score, console_type="ntsc", level=None):
        try:
            score = int(score.replace(",", ""))
            if level is not None:
                level = int(level)
        except ValueError:
            raise CommandException(send_usage=True)

        if score < 0:
            raise CommandException("Invalid PB.")

        # I no longer feel comfortable setting a limit here, beyond "8 digits."
        # Even that upper bound, I implement knowing it may someday be broken.
        # I cannot predict the future of this game, nor do I wish to try.
        # Kudos to those who push the limits of what is possible.
        if score > 10 ** 8 - 1:
            raise CommandException("Not yet...")

        if level is not None and (level < 0 or level > 29):
            raise CommandException("Invalid level.")

        console_type = console_type.lower()
        if console_type != "ntsc" and console_type != "pal":
            raise CommandException("Invalid PB type - must be NTSC or PAL (default NTSC)")

        # TODO: remove if people abuse
        if score > 10 ** 7 - 1:
            self.send_message("You wish, kid >.>... just kidding!")

        level_text = ""
        if level is not None:
            level_text = f" level {level}"

        pb = self.context.user.add_pb(score, console_type=console_type, starting_level=level)
        self.send_message("{user_tag} has a new {console_type}{level_text} PB of {score:,}!".format(
            user_tag=self.context.user_tag,
            console_type=pb.get_console_type_display(),
            level_text=level_text,
            score=pb.score
        ))
