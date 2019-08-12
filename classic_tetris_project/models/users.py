import asyncio
import re
from datetime import datetime

from django.db import models
# Used to add User upon creation of TwitchUser or DiscordUser
from django.db.models import signals
from django.dispatch import receiver

from .. import twitch, discord
from ..util import memoize
from ..countries import countries

class User(models.Model):
    RE_PREFERRED_NAME = re.compile(r"^[A-Za-z0-9\-_. ]+$")

    preferred_name = models.CharField(max_length=64, null=True)
    ntsc_pb = models.IntegerField(null=True)
    ntsc_pb_updated_at = models.DateTimeField(null=True)
    pal_pb = models.IntegerField(null=True)
    pal_pb_updated_at = models.DateTimeField(null=True)
    country = models.CharField(max_length=3, null=True)

    def set_pb(self, pb, pb_type="ntsc"):
        if pb_type == "pal":
            self.pal_pb = pb
            self.pal_pb_updated_at = datetime.now()
            self.save()
            return True
        elif pb_type == "ntsc":
            self.ntsc_pb = pb
            self.ntsc_pb_updated_at = datetime.now()
            self.save()
            return True
        else:
            return False

    def set_country(self, country_code):
        if country_code.upper() in countries:
            self.country = country_code.upper()
            self.save()
            return True
        else:
            return False

    def set_preferred_name(self, name):
        if User.RE_PREFERRED_NAME.match(name):
            self.preferred_name = name
            self.save()
            return True
        else:
            return False

    def merge(self, target_user):
        from ..util.merge import UserMerger
        UserMerger(self, target_user).merge()


class PlatformUser(models.Model):

    class Meta:
        abstract = True

    # Create User foreign key before saving
    @staticmethod
    def before_save(sender, instance, **kwargs):
        if instance.user_id is None:
            user = User()
            user.save()
            instance.user = user

    def unlink_from_user(self):
        self.user_id = None
        self.save()


class TwitchUser(PlatformUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="twitch_user")
    twitch_id = models.CharField(max_length=64, unique=True, blank=False)
    """
    username is set when:
    - a TwitchUser with no username is saved
    - a TwitchUser runs a command
    - TwitchUser.from_username is called
    """
    username = models.CharField(max_length=25, unique=True, blank=False)

    @staticmethod
    def fetch_by_twitch_id(twitch_id):
        twitch_user, created = TwitchUser.objects.get_or_create(twitch_id=twitch_id)
        return twitch_user

    @staticmethod
    def from_username(username):
        try:
            twitch_user = TwitchUser.objects.get(username__iexact=username)
            return twitch_user
        except TwitchUser.DoesNotExist:
            user_obj = twitch.API.user_from_username(username)
            if user_obj:
                twitch_user = TwitchUser.fetch_by_twitch_id(user_obj.id)
                twitch_user.update_username(user_obj.username)
                return twitch_user
            else:
                return None

    @property
    @memoize
    def user_obj(self):
        return twitch.client.get_user(self.twitch_id)

    @property
    def user_tag(self):
        return f"@{self.username}"

    def send_message(self, message):
        self.user_obj.send_message(message)

    def update_username(self, username):
        if self.username != username:
            self.username = username
            self.save()

    @staticmethod
    def before_save(sender, instance, **kwargs):
        if not instance.username:
            instance.username = instance.user_obj.username

        PlatformUser.before_save(sender, instance, **kwargs)

    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_memo_")}
    def __setstate__(self, state):
        self.__dict__.update(state)


class DiscordUser(PlatformUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="discord_user")
    discord_id = models.CharField(max_length=64, unique=True, blank=False)

    @staticmethod
    def fetch_by_discord_id(discord_id):
        discord_user, created = DiscordUser.objects.get_or_create(discord_id=discord_id)
        return discord_user

    @property
    @memoize
    def user_obj(self):
        return discord.client.get_user(int(self.discord_id))

    @property
    def username(self):
        return self.user_obj.name

    @property
    def user_tag(self):
        return f"<@{self.discord_id}>"

    def send_message(self, message):
        asyncio.run_coroutine_threadsafe(
            self.user_obj.send(message), 
            discord.client.loop
        )


signals.pre_save.connect(DiscordUser.before_save, sender=DiscordUser)
signals.pre_save.connect(TwitchUser.before_save, sender=TwitchUser)
