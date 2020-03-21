from .command import Command, CommandException
from .. import discord

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

        # Get Discord nickname if it exists
        try:
            name = self.context.guild.get_member(int(platform_user.discord_id)).display_name
        except AttributeError:
            name = platform_user.username

        ntsc_exists = False
        pal_exists = False

        if user.ntsc_pb or user.ntsc_pb_19:
            ntsc_exists = True
            if not user.ntsc_pb_19:
                ntsc_pb = "{pb:,}".format(pb=user.ntsc_pb)
            elif not user.ntsc_pb:
                ntsc_pb = "{pb:,} ({pb:,} 19 start)".format(pb=user.ntsc_pb_19)
            else:
                ntsc_pb = "{pb:,} ({pb19:,} 19 start)".format(pb=user.ntsc_pb, pb19=user.ntsc_pb_19)

        if user.pal_pb:
            pal_exists = True

        if ntsc_exists and pal_exists:
            self.send_message("{name} has an NTSC PB of {ntsc} and a PAL PB of {pal:,}.".format(
                name=name,
                ntsc=ntsc_pb,
                pal=user.pal_pb
            ))
        else:
            if ntsc_exists:
                self.send_message("{name} has an NTSC PB of {ntsc}.".format(
                    name=name,
                    ntsc=ntsc_pb
                ))
            elif pal_exists:
                self.send_message("{name} has a PAL PB of {pb:,}.".format(
                    name=name,
                    pb=user.pal_pb
                ))
            else:
                self.send_message("User has not set a PB.")


@Command.register("newpb", "setpb",
                  usage="setpb <pb> [type=NTSC]")
class SetPBCommand(Command):
    def execute(self, pb, pb_type="ntsc"):
        try:
            pb = int(pb.replace(",", ""))
        except ValueError:
            raise CommandException(send_usage=True)

        pb_type = pb_type.lower()

        if pb < 0:
            self.send_message("Invalid PB.")
        elif pb > 1400000:
            self.send_message("You wish, kid >.>")
        else:
            if self.context.user.set_pb(pb, pb_type):
                self.send_message("{user_tag} has a new {pb_type} PB of {pb:,}!".format(
                    user_tag=self.context.user_tag,
                    pb_type=pb_type.upper(),
                    pb=pb
                ))
            else:
                self.send_message("Invalid PB type - must be NTSC or PAL (default NTSC)")
