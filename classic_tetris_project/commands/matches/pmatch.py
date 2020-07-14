from django.db.models import F, Max
from django.db.models.functions import Abs

from ..command import Command, CommandException
from ...models import User
from ... import twitch

@Command.register_twitch("pmatch",
                         usage="pmatch [user] [results=3]")
class MatchCommand(Command):
    MIN_RESULTS = 3
    DEFAULT_RESULTS = 3
    MAX_RESULTS = 6
    def execute(self, target_name=None, num_results=None):
        self.check_public()
        target, num_results = self.parse_args(target_name, num_results)

        target_pb = target.user.get_pb("pal")
        if not target_pb:
            raise CommandException(f"{target.username} has not set a PB.")

        closest_users = self.closest_users_with_pbs(target.user, target_pb, num_results)
        match_message = "Closest PAL opponents for {username} ({pb:,}): {matches}".format(
            username=target.username,
            pb=target_pb,
            matches=", ".join(
                [f"{user.twitch_user.username} ({pb:,})" for user, pb in closest_users]
            )
        )
        self.send_message(match_message)

    def parse_args(self, target_name, num_results):
        if target_name is None: # No arguments were passed
            target = self.context.user.twitch_user
            num_results = self.DEFAULT_RESULTS

        elif num_results is None: # One argument was passed
            try:
                num_results = int(target_name)
                target = self.context.user.twitch_user
            except ValueError:
                target = self.twitch_user_from_username(target_name)
                num_results = self.DEFAULT_RESULTS

        else: # Two arguments were passed
            try:
                num_results = int(num_results)
            except ValueError:
                raise CommandException("Invalid arguments.", send_usage=True)

            target = self.twitch_user_from_username(target_name)

        if not target:
            raise CommandException("That user doesn't exist.")

        # Constraining num_results to range
        num_results = min(num_results, self.MAX_RESULTS)
        num_results = max(num_results, self.MIN_RESULTS)

        return (target, num_results)


    def closest_users_with_pbs(self, target_user, target_pb, n):
        # TODO: Handle PAL too?
        usernames = twitch.API.usernames_in_channel(self.context.channel.name)

        user_ids_with_pbs = (User.objects
                             .filter(twitch_user__username__in=usernames,
                                     score_pb__current=True,
                                     score_pb__console_type="pal")
                             .values("id")
                             .annotate(pb=Max("score_pb__score"))
                             .exclude(pb=0)
                             .exclude(id=target_user.id)
                             .order_by(Abs(F("pb") - target_pb).asc())
                             )[:n]
        users = { user.id: user for user in list(
            User.objects.filter(id__in=[row["id"] for row in user_ids_with_pbs])
            .select_related("twitch_user")
        ) }
        return sorted([(users[row["id"]], row["pb"]) for row in user_ids_with_pbs],
                      key=lambda row: row[1])
