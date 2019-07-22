from .command import Command, CommandException, register_command
from ..util import Platform

@register_command("pb", "getpb")
class GetPBCommand(Command):
    usage = "pb [username] (default username you)"

    def execute(self, username=None):
        if self.context.platform == Platform.DISCORD:
            platform_user = (Command.discord_user_from_username(username) if username
                             else self.context.platform_user)
        elif self.context.platform == Platform.TWITCH:
            platform_user = (Command.twitch_user_from_username(username) if username
                             else self.context.platform_user)


        if not platform_user:
            self.send_message("User has not set a PB.")
            return

        user = platform_user.user
        if user.ntsc_pb and user.pal_pb:
            self.send_message("{user_tag} has an NTSC PB of {ntsc:,} and a PAL PB of {pal:,}.".format(
                user_tag=platform_user.user_tag,
                ntsc=user.ntsc_pb,
                pal=user.pal_pb
            ))

        else:
            if user.ntsc_pb:
                self.send_message("{user_tag} has an NTSC PB of {ntsc:,}.".format(
                    user_tag=platform_user.user_tag,
                    ntsc=user.ntsc_pb
                ))
            elif user.pal_pb:
                self.send_message("{user_tag} has a PAL PB of {pb:,}.".format(
                    user_tag=platform_user.user_tag,
                    pb=user.pal_pb
                ))
            else:
                self.send_message("User has not set a PB.")
