from .command import Command, CommandException

@Command.register("pb", "getpb",
                  usage="pb [username] (default username you)")
class GetPBCommand(Command):
    def execute(self, *username):
        username = username[0] if len(username) == 1 else self.context.args_string
        platform_user = (self.platform_user_from_username(username) if username
                         else self.context.platform_user)

        if not platform_user:
            self.send_message("User has not set a PB.")
            return

        user = platform_user.user

        ntsc, pal = False

        if user.ntsc_pb or user.ntsc_pb_19:
            ntsc = True
            if not user.ntsc_pb_19:
                ntsc_pb = "{pb:,}".format(pb=user.ntsc_pb)
            elif not user.ntsc_pb:
                ntsc_pb = "{pb:,} ({pb:,} 19 start)".format(pb=user.ntsc_pb_19)
            else:
                ntsc_pb = "{pb:,} ({pb19:,} 19 start)".format(pb=user.ntsc_pb, pb19=user.ntsc_pb_19)

        if user.pal_pb:
            pal = True

        if ntsc or pal:
            self.send_message("{user_tag} has an NTSC PB of {ntsc} and a PAL PB of {pal:,}.".format(
                user_tag=platform_user.user_tag,
                ntsc=ntsc_pb,
                pal=user.pal_pb
            ))
        else:
            if ntsc:
                self.send_message("{user_tag} has an NTSC PB of {ntsc}.".format(
                    user_tag=platform_user.user_tag,
                    ntsc=ntsc_pb
                ))
            elif pal:
                self.send_message("{user_tag} has a PAL PB of {pb:,}.".format(
                    user_tag=platform_user.user_tag,
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
                self.send_message("{user_tag} has a new {pb_type} pb of {pb:,}!".format(
                    user_tag=self.context.user_tag,
                    pb_type=pb_type.upper(),
                    pb=pb
                ))
            else:
                self.send_message("Invalid PB type - must be NTSC or PAL (default NTSC)")
