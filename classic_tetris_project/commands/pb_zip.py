from io import BytesIO
import zipfile
from .command import Command, CommandException
from ..models.users import TwitchUser

@Command.register_discord("obsfiles", usage="obsfiles [type=ntsc]")
class ZipFileCommand(Command):

    def execute(self, pb_type="ntsc"):

        self.check_moderator()

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED, False) as z:
            for twitch_user in TwitchUser.objects.all():
                pb = twitch_user.user.get_pb(pb_type)

                if pb is not None:
                    name = f"{twitch_user.username}_{pb_type}_pb.txt"
                    contents = "{n:,}".format(n=pb)
                    z.writestr(name, contents)

                    name = f"{twitch_user.username}_playstyle.txt"
                    contents = ""
                    if twitch_user.user.playstyle is not None:
                        contents = twitch_user.user.playstyle[:3].upper()
                        contents = contents if contents != "HYP" else "TAP"
                    z.writestr(name, contents)

        buffer.seek(0)
        self.context.send_file(buffer, "pbs.zip")



