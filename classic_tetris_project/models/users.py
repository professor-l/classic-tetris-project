from django.db import models

# Used to add User upon creation of TwitchUser or DiscordUser
from django.db.models import signals
from django.dispatch import receiver

class User(models.Model):
    preferred_name = models.CharField(max_length=64, null=True)
    ntsc_pb = models.IntegerField(null=True)
    pal_pb = models.IntegerField(null=True)
    country = models.CharField(max_length=3, null=True)

    def set_pb(self, pb, pb_type="ntsc"):
        if pb_type == "pal":
            self.pal_pb = pb
            self.save()
            return True
        elif pb_type == "ntsc":
            self.ntsc_pb = pb
            self.save()
            return True
        else:
            return False


class PlatformUser(models.Model):

    # Foreign key referencing User, delete this if said User is deleted
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    # Create User foreign key before saving
    @staticmethod
    def before_save(sender, instance, **kwargs):
        if instance.user_id is None:
            user = User()
            user.save()
            instance.user = user


class TwitchUser(PlatformUser):
    twitch_id = models.CharField(max_length=64, unique=True, blank=False)

    @staticmethod
    def fetch_by_twitch_id(twitch_id):
        twitch_user, created = TwitchUser.objects.get_or_create(twitch_id=twitch_id)
        return twitch_user

    @property
    def user_tag(self):
        # TODO
        raise NotImplementedError


class DiscordUser(PlatformUser):
    discord_id = models.CharField(max_length=64, unique=True, blank=False)

    @staticmethod
    def fetch_by_discord_id(discord_id):
        discord_user, created = DiscordUser.objects.get_or_create(discord_id=discord_id)
        return discord_user

    @property
    def user_tag(self):
        return f"<@{self.discord_id}>"


signals.pre_save.connect(PlatformUser.before_save, sender=DiscordUser)
signals.pre_save.connect(PlatformUser.before_save, sender=TwitchUser)
