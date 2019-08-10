from django.db import transaction

class UserMerger:
    def __init__(self, user1, user2):
        self.user1 = user1
        self.user2 = user2

    @transaction.atomic
    def merge(self):
        self.update_user_fields()
        self.update_platform_users()

        self.user2.delete()

    def update_user_fields(self):
        self.user1.preferred_name = self.user1.preferred_name or self.user2.preferred_name

        if self.user1.ntsc_pb is None or (self.user2.ntsc_pb is not None and
                                          self.user2.ntsc_pb > self.user1.ntsc_pb):
            self.user1.ntsc_pb = self.user2.ntsc_pb
        if self.user1.pal_pb is None or (self.user2.pal_pb is not None and
                                         self.user2.pal_pb > self.user1.pal_pb):
            self.user1.pal_pb = self.user2.pal_pb

        self.user1.country = self.user1.country or self.user2.country
        self.user1.save()

    def update_platform_users(self):
        if hasattr(self.user2, "twitch_user"):
            self.user2.twitch_user.user = self.user1
            self.user2.twitch_user.save()
        if hasattr(self.user2, "discord_user"):
            self.user2.discord_user.user = self.user1
            self.user2.discord_user.save()
