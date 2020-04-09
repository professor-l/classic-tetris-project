from .command import Command, CommandException
from .. import discord
from ..util import Platform
from ..models import DiscordUser

@Command.register("pb", "getpb",
                  usage="pb [username] (default username you)")
class GetPBCommand(Command):
    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        if username and not self.any_platform_user_from_username(username):
            raise CommandException("User has not set a PB.")

        platform_user = (self.any_platform_user_from_username(username) if username
                         else self.context.platform_user)

        if not platform_user:
            raise CommandException("Invalid specified user.")

        user = platform_user.user
        name = self.context.display_name(platform_user)

        ntsc_pb = user.get_pb("ntsc")
        ntsc_pb_19 = user.get_pb("ntsc", 19)
        pal_pb = user.get_pb("pal")

        if ntsc_pb:
            if ntsc_pb_19:
                ntsc_pb_text = "{pb:,} ({pb19:,} 19 start)".format(pb=ntsc_pb, pb19=ntsc_pb_19)
            else:
                ntsc_pb_text = "{pb:,}".format(pb=ntsc_pb)

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


@Command.register("newpb", "setpb",
                  usage="setpb <score> [type=NTSC] [level]")
class SetPBCommand(Command):
    def execute(self, score, console_type="ntsc", level=None):
        try:
            score = int(score.replace(",", ""))
            if level is not None:
                level = int(level)
        except ValueError:
            raise CommandException(send_usage=True)

        if score < 0:
            raise CommandException("Invalid PB.")

        if score > 1400000:
            raise CommandException("You wish, kid >.>")

        if level is not None and (level < 0 or level > 29):
            raise CommandException("Invalid level.")

        console_type = console_type.lower()
        if console_type != "ntsc" and console_type != "pal":
            raise CommandException("Invalid PB type - must be NTSC or PAL (default NTSC)")

        pb = self.context.user.add_pb(score, console_type=console_type, starting_level=level)
        self.send_message("{user_tag} has a new {console_type} PB of {score:,}!".format(
            user_tag=self.context.user_tag,
            console_type=pb.get_console_type_display(),
            score=pb.score
        ))
