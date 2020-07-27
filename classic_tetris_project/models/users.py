import asyncio
import discord as discordpy
import re
from django.conf import settings
from django.contrib.auth.models import User as AuthUser
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from furl import furl

from .. import twitch, discord
from ..util import lazy
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

    preferred_name = models.CharField(max_length=64, null=True, blank=True)

    pronouns = models.CharField(max_length=16, null=True, blank=True,
                                choices=PRONOUN_CHOICES.items())

    playstyle = models.CharField(max_length=16, null=True, blank=True,
                                 choices=PLAYSTYLE_CHOICES.items())

    country = models.CharField(max_length=3, null=True, blank=True,
                               choices=[(country.abbreviation, country.full_name) for country in Country.ALL])

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

    @lazy
    def display_name(self):
        if self.preferred_name:
            return self.preferred_name
        elif hasattr(self, "twitch_user"):
            return self.twitch_user.username
        elif hasattr(self, "discord_user"):
            return self.discord_user.display_name()
        else:
            return f"User {self.id}"

    def merge(self, target_user):
        from ..util.merge import UserMerger
        UserMerger(self, target_user).merge()

    def profile_id(self):
        if hasattr(self, "twitch_user"):
            return self.twitch_user.username
        else:
            return self.id

    def __str__(self):
        if hasattr(self, "twitch_user"):
            return self.twitch_user.username
        else:
            return f"User<id={self.id}>"

    def get_absolute_url(self, include_base=False):
        path = reverse("user", kwargs={ "id": self.profile_id() })
        if include_base:
            return furl(settings.BASE_URL, path=path).url
        else:
            return path


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
    twitch_id = models.CharField(max_length=64, unique=True, blank=False) # unique index
    """
    username is set when:
    - a TwitchUser with no username is saved
    - a TwitchUser runs a command
    - TwitchUser.from_username is called with fetch=True
    """
    username = models.CharField(max_length=25, unique=True, blank=False) # unique index

    @staticmethod
    def fetch_by_twitch_id(twitch_id):
        try:
            return TwitchUser.objects.get(twitch_id=twitch_id)
        except TwitchUser.DoesNotExist:
            return None

    @staticmethod
    def fetch_or_create_by_twitch_id(twitch_id):
        twitch_user, created = TwitchUser.objects.get_or_create(twitch_id=twitch_id)
        return twitch_user

    @staticmethod
    def from_username(username, refetch=False):
        """
        If refetch is True and we can't find a TwitchUser with the given username, query Twitch's
        API to check if an existing TwitchUser updated their username
        """
        try:
            twitch_user = TwitchUser.objects.get(username__iexact=username)
            return twitch_user
        except TwitchUser.DoesNotExist:
            if refetch:
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
                twitch_user = TwitchUser.get_or_create_from_user_obj(user_obj)

        if twitch_user is None:
            raise Exception(f"No Twitch account exists with username '{username}'.")
        return twitch_user

    @staticmethod
    def get_or_create_from_user_obj(user_obj):
        try:
            twitch_user = TwitchUser.objects.get(twitch_id=str(user_obj.id))
            twitch_user.update_username(user_obj.username)
            return twitch_user
        except TwitchUser.DoesNotExist:
            return TwitchUser.objects.create(
                twitch_id=str(user_obj.id),
                username=user_obj.username
            )


    @lazy
    def user_obj(self):
        return twitch.client.get_user(self.twitch_id)

    def display_name(self):
        return self.username

    @property
    def user_tag(self):
        return f"@{self.username}"

    @property
    def twitch_url(self):
        return f"https://www.twitch.tv/{self.username}"

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
    username = models.CharField(max_length=32, blank=False)
    discriminator = models.CharField(max_length=4, blank=False)

    class Meta:
        constraints = [
            # Implicit indexes on these columns
            models.UniqueConstraint(fields=["username", "discriminator"],
                                    name="unique_username_discriminator"),
        ]

    @staticmethod
    def get_or_create_from_user_obj(user_obj):
        try:
            discord_user = DiscordUser.objects.get(discord_id=str(user_obj.id))
            discord_user.update_fields(user_obj)
            return discord_user
        except DiscordUser.DoesNotExist:
            return DiscordUser.objects.create(
                discord_id=str(user_obj.id),
                username=user_obj.name,
                discriminator=user_obj.discriminator
            )

    @lazy
    def user_obj(self):
        if discord.client.is_ready():
            user = discord.client.get_user(int(self.discord_id))
        else:
            user = discord.API.user_from_id(self.discord_id)

        if user:
            self.update_fields(user)

        return user

    def update_fields(self, user_obj):
        if str(user_obj.id) != self.discord_id:
            raise Exception("got wrong discord id")
        # Only bother updating if name or discriminator have changed
        if self.username != user_obj.name or self.discriminator != user_obj.discriminator:
            self.username = user_obj.name
            self.discriminator = user_obj.discriminator
            self.save()

    def display_name(self, guild=None):
        if guild:
            return guild.get_member(int(self.discord_id)).display_name
        else:
            return self.username

    @property
    def user_tag(self):
        return f"<@{self.discord_id}>"

    @property
    def username_with_discriminator(self):
        return f"{self.username}#{self.discriminator}"

    def send_message(self, message):
        if not isinstance(self.user_obj, discordpy.User):
            raise Exception("can't send message from this context")
        # TODO run this in an async task that's guaranteed to have a discord client connection
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
