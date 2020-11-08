import csv
from django.core.cache import cache

from .command import Command, CommandException
from ..models import User


@Command.register_discord("export", usage="export")
class ExportDatabaseCommand(Command):
    def execute(self, *args):
        self.check_private()

        if cache.get("pbcsv"):
            self.context.send_file("cache/pbs.csv")
            return

        fields = ["twitch_id", "twitch_username",
                  "ntsc_pb", "ntsc_pb_updated_at",
                  "pal_pb", "pal_pb_updated_at",
                  "country_code", "country",
                  "nickname"]

        with open("cache/pbs.csv", "w") as file:

            writer = csv.DictWriter(file, fieldnames=fields)

            for user in User.objects.all():
                if not hasattr(user, "twitch_user"):
                    continue

                ntsc = user.get_pb_object(console_type="ntsc")
                ntscpb = ntsc.score if ntsc else None
                ntscts = ntsc.created_at if ntsc else None
                pal = user.get_pb_object(console_type="pal")
                palpb = pal.score if pal else None
                palts = pal.created_at if pal else None

                d = {
                    "twitch_id": user.twitch_user.twitch_id,
                    "twitch_username": user.twitch_user.username,
                    "nickname": user.preferred_name or None,
                    "country_code": user.country or None,
                    "country": user.get_country(),
                    "ntsc_pb": ntscpb,
                    "ntsc_pb_updated_at": ntscts,
                    "pal_pb": palpb,
                    "pal_pb_updated_at": palts,
                }

                writer.writerow(d)

        self.context.send_file("cache/pbs.csv")
        cache.set("pbcsv", True, timeout=24*60*60)

