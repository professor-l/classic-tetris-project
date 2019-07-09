from .command import Command, ArgException, register_command
from ..util import comma_separate

@register_command("newpb", "setpb")
class SetPBCommand(Command):
    USAGE = "setpb <pb> <type> (default type NTSC)"

    def execute(self, pb, pb_type="ntsc", *args):
        if args:
            self.send_usage()
            return

        try:
            pb = int(pb.replace(",", ""))
        except ValueError:
            self.send_usage()
            return

        pb_type = pb_type.lower()

        if pb < 0:
            self.send_message("Invalid PB.")
        elif pb > 1400000:
            self.send_message("You wish, kid")
        else:
            try:
                self.context.user.set_pb(pb, pb_type)
                self.send_message("{user_tag} has a new {pb_type} pb of {pb}!".format(
                    user_tag=self.context.user_tag,
                    pb_type=pb_type.upper(),
                    pb=comma_separate(pb)
                ))
            except Exception as e:
                print(e)
                self.send_message("Invalid PB type - must be NTSC or PAL (default NTSC)")
