import asyncio
import re

from django.contrib.auth.models import User as AuthUser
from django.db import models
# Used to add User upon creation of TwitchUser or DiscordUser
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

from .. import twitch, discord
from ..util import memoize
from ..countries import Country

class User(models.Model):
    RE_PREFERRED_NAME = re.compile(r"^[A-Za-z0-9\-_. ]+$")

    PRONOUN_CHOICES = {
        "he": "He/him/his",
        "she": "She/her/hers",
        "they": "They/them/theirs",
    }

    PLAYSTYLE_CHOICES = {
        "das": "DAS",
        "hypertap": "Hypertap",
        "hybrid": "Hybrid",
    }

    preferred_name = models.CharField(max_length=64, null=True)

    pronouns = models.CharField(max_length=16, null=True, choices=PRONOUN_CHOICES.items())

    playstyle = models.CharField(max_length=16, null=True, choices=PLAYSTYLE_CHOICES.items())

    country = models.CharField(max_length=3, null=True)

    same_piece_sets = models.BooleanField(default=False)

    def add_pb(self, score, console_type="ntsc", starting_level=None, lines=None):
        from .scores import ScorePB
        return ScorePB.log(self, score=score, console_type=console_type.lower(),
                           starting_level=starting_level, lines=lines)

    def get_pb(self, console_type="ntsc", starting_level=None):
        scope = self.score_pbs.filter(console_type=console_type, current=True)
        if starting_level is not None:
            scope = scope.filter(starting_level=starting_level)
        score_pb = scope.order_by("-score").first()
        return score_pb.score if score_pb else None

    def set_pronouns(self, pronoun):
        pronoun = pronoun.lower()
        if pronoun in self.PRONOUN_CHOICES:
            self.pronouns = pronoun
            self.save()
            return True
        else:
            return False

    def set_playstyle(self, style):
        style = style.lower()
        if style in self.PLAYSTYLE_CHOICES:
            self.playstyle = style
            self.save()
            return True
        else:
            return False

    def set_country(self, country):
        country = Country.get_country(country)
        if country is not None:
            self.country = country.abbreviation
            self.save()
            return True
        else:
            return False

    def get_country(self):
        return Country.get_country(self.country)

    def set_preferred_name(self, name):
        if User.RE_PREFERRED_NAME.match(name):
            self.preferred_name = name
            self.save()
            return True
        else:
            return False

    def set_same_piece_sets(self, value):
        accepted_y = ["true", "yes", "y", "t"]
        accepted_n = ["false", "no", "n", "f"]
        if value in accepted_y:
            value = True
        elif value in accepted_n:
            value = False

        else:
            return False

        self.same_piece_sets = value
        self.save()
        return True

    @property
    @memoize
    def display_name(self):
        if self.preferred_name:
            return self.preferred_name
        elif hasattr(self, "twitch_user"):
            return self.twitch_user.username
        elif hasattr(self, "discord_user"):
            return self.discord_user.display_name()

    def merge(self, target_user):
        from ..util.merge import UserMerger
        UserMerger(self, target_user).merge()

    def __str__(self):
        if hasattr(self, "twitch_user"):
            return self.twitch_user.username
        else:
            return f"User<id={self.id}>"


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
        try:
            return TwitchUser.objects.get(twitch_id=twitch_id)
        except TwitchUser.DoesNotExist:
            return None

    def fetch_or_create_by_twitch_id(twitch_id):
        twitch_user, created = TwitchUser.objects.get_or_create(twitch_id=twitch_id)
        return twitch_user

    @staticmethod
    def from_username(username):
        try:
            twitch_user = TwitchUser.objects.get(username__iexact=username)
            return twitch_user
        except TwitchUser.DoesNotExist:
            user_obj = twitch.API.user_from_username(username)
            if user_obj is not None:
                twitch_user = TwitchUser.fetch_by_twitch_id(user_obj.id)
                if twitch_user is not None:
                    twitch_user.update_username(user_obj.username)
                    return twitch_user

            return None

    @staticmethod
    def get_or_create_from_username(username):
        twitch_user = TwitchUser.from_username(username)

        if twitch_user is None:
            user_obj = twitch.API.user_from_username(username)
            if user_obj is not None:
                twitch_user = TwitchUser.fetch_or_create_by_twitch_id(user_obj.id)

        if twitch_user is None:
            raise Exception(f"No Twitch account exists with username '{username}'.")
        return twitch_user


    @property
    @memoize
    def user_obj(self):
        return twitch.client.get_user(self.twitch_id)

    def display_name(self):
        return self.username

    @property
    def user_tag(self):
        return f"@{self.username}"

    def send_message(self, message):
        self.user_obj.send_message(message)

    def update_username(self, username):
        if self.username != username:
            self.username = username
            self.save()
            if hasattr(self, "channel") and self.channel.connected:
                self.channel.summon_bot()

    def get_or_create_channel(self):
        if hasattr(self, "channel"):
            return self.channel
        else:
            from .twitch import TwitchChannel
            channel = TwitchChannel(twitch_user=self)
            channel.save()
            return channel

    @staticmethod
    def before_save(sender, instance, **kwargs):
        if not instance.username:
            instance.username = instance.user_obj.username

        PlatformUser.before_save(sender, instance, **kwargs)

    def __getstate__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_memo_")}
    def __setstate__(self, state):
        self.__dict__.update(state)

    def __str__(self):
        return self.username

signals.pre_save.connect(TwitchUser.before_save, sender=TwitchUser)


class DiscordUser(PlatformUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="discord_user")
    discord_id = models.CharField(max_length=64, unique=True, blank=False)
    username = models.CharField(max_length=32, null=True) # nullable for now, we might change this later

    @staticmethod
    def fetch_by_discord_id(discord_id):
        discord_user, created = DiscordUser.objects.get_or_create(discord_id=discord_id)
        return discord_user

    @property
    @memoize
    def user_obj(self):
        # TODO use Discord's HTTP API
        if not discord.client.is_ready():
            return None
        user = discord.client.get_user(int(self.discord_id))

        # Temporary critical fix for username bug in db
        # self.username = user.name # Update our username while we're getting this
        # self.save()
        return user

    def display_name(self, guild=None):
        if guild:
            return guild.get_member(int(self.discord_id)).display_name
        else:
            return self.username or (self.user_obj and self.user_obj.name)

    @property
    def user_tag(self):
        return f"<@{self.discord_id}>"

    def send_message(self, message):
        asyncio.run_coroutine_threadsafe(
            self.user_obj.send(message),
            discord.client.loop
        )

signals.pre_save.connect(DiscordUser.before_save, sender=DiscordUser)


class WebsiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="website_user")
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, related_name="website_user")

    @staticmethod
    def fetch_by_user(user, username=None):
        """
        Creates or fetches a WebsiteUser from a given User object.
        If the WebsiteUser does not exist, the given username is used for the
        new auth User.
        """
        try:
            return WebsiteUser.objects.get(user=user)
        except WebsiteUser.DoesNotExist:
            username = username or f"user_{user.id}"
            auth_user = AuthUser.objects.create_user(username=username)
            return WebsiteUser.objects.create(user=user, auth_user=auth_user)
