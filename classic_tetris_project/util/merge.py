from django.db import transaction
from ..models import Game, Match, ScorePB

class UserMerger:
    def __init__(self, user1, user2):
        """
        Always keep the user associated with the DiscordUser if possible
        Everything is merged into user1; user2 is deleted
        """
        if hasattr(user1, "discord_user"):
            self.user1 = user1
            self.user2 = user2
        else:
            self.user1 = user2
            self.user2 = user1

    @transaction.atomic
    def merge(self):
        self.update_user_fields()
        self.update_platform_users()
        self.update_related_models()

        self.user2.delete()

    def update_user_fields(self):
        self.user1.preferred_name = self.user1.preferred_name or self.user2.preferred_name
        self.user1.country = self.user1.country or self.user2.country
        self.user1.save()

    def update_platform_users(self):
        if hasattr(self.user2, "twitch_user"):
            self.user2.twitch_user.user = self.user1
            self.user2.twitch_user.save()
        if hasattr(self.user2, "discord_user"):
            self.user2.discord_user.user = self.user1
            self.user2.discord_user.save()

    def update_related_models(self):
        ScorePB.objects.filter(user=self.user2).update(user=self.user1)
        Match.objects.filter(player1=self.user2).update(player1=self.user1)
        Match.objects.filter(player2=self.user2).update(player2=self.user1)
        Game.objects.filter(winner=self.user2).update(winner=self.user1)
