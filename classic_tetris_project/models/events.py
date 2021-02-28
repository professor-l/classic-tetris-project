from django.conf import settings
from django.db import models
from django.urls import reverse
from furl import furl
from markdownx.models import MarkdownxField

from ..facades import qualifying_types


class Event(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(db_index=True)
    qualifying_type = models.IntegerField(choices=qualifying_types.CHOICES)
    qualifying_open = models.BooleanField(default=False)
    pre_qualifying_instructions = MarkdownxField(blank=True)
    qualifying_instructions = MarkdownxField(blank=True)
    event_info = MarkdownxField(blank=True)

    def is_user_eligible(self, user):
        return self.user_ineligible_reason(user) is None

    # Returns the reason a user is ineligible to qualify for this event. Returns None if they are
    # eligible.
    def user_ineligible_reason(self, user):
        from .qualifiers import Qualifier
        if not self.qualifying_open:
            return "closed"
        if not user:
            return "logged_out"
        if Qualifier.objects.filter(event=self, user=user, submitted=True).exists():
            return "already_qualified"
        if not hasattr(user, "twitch_user"):
            return "link_twitch"
        if not hasattr(user, "discord_user"):
            return "link_discord"
        return None

    def get_absolute_url(self, include_base=False):
        path = reverse("event:index", args=[self.slug])
        if include_base:
            return furl(settings.BASE_URL, path=path).url
        else:
            return path

    def __str__(self):
        return self.name
