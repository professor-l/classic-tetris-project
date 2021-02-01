from django.conf import settings
from django.contrib import admin, auth
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django_object_actions import DjangoObjectActions
from markdownx.admin import MarkdownxModelAdmin

from ..models import User, DiscordUser, TwitchUser, WebsiteUser, Match, Game, TwitchChannel, CustomCommand, Page, Event, Qualifier


class DiscordUserInline(admin.StackedInline):
    model = DiscordUser

class TwitchUserInline(admin.StackedInline):
    model = TwitchUser

class WebsiteUserInline(admin.StackedInline):
    model = WebsiteUser

@admin.register(User)
class UserAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [DiscordUserInline, TwitchUserInline, WebsiteUserInline]

    # Don't allow this on production as this is a security vulnerability
    if settings.DEBUG:
        def login_as(self, request, user):
            website_user = WebsiteUser.fetch_by_user(user)
            auth.login(request, website_user.auth_user)
            return redirect(reverse("index"))

        change_actions = ("login_as",)

@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    list_display = ("username", "discriminator", "discord_id")

@admin.register(TwitchUser)
class TwitchUserAdmin(admin.ModelAdmin):
    list_display = ("username", "twitch_id")
    search_fields = ("username",)


class GameInline(admin.TabularInline):
    model = Game

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [GameInline]
    list_display = ('__str__', 'player1', 'wins1', 'player2', 'wins2', 'channel', 'ended_at')


class CustomCommandInline(admin.TabularInline):
    model = CustomCommand

@admin.register(TwitchChannel)
class TwitchChannelAdmin(admin.ModelAdmin):
    inlines = [CustomCommandInline]
    list_display = ("twitch_user", "connected")
    search_fields = ("twitch_user__username",)
    autocomplete_fields = ("twitch_user",)


@admin.register(Page)
class PageAdmin(MarkdownxModelAdmin):
    prepopulated_fields = { "slug": ("title",) }
    list_display = ("title", "slug", "public", "updated_at")


@admin.register(Event)
class EventAdmin(MarkdownxModelAdmin):
    prepopulated_fields = { "slug": ("name",) }
    list_display = ("name", "qualifying_open")

@admin.register(Qualifier)
class QualifierAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "qualifying_score", "approved", "reviewed_at")
    list_filter = ("approved",)

    fieldsets = (
        ("Qualifier Data", {
            "fields": ("user", "event", "qualifying_type", "qualifying_score", "qualifying_data",
                       "vod", "auth_word", "details", "created_at", "submitted", "submitted_at"),
        }),
        ("Moderator Data", {
            "fields": ("approved", "reviewed_by", "reviewed_at", "review_data"),
            "description": ("Qualifiers can be reviewed from <a href='/review_qualifiers/'>this "
                            "page</a>. Change Approved to \"Unknown\" to allow a qualifier to be "
                            "reviewed again.")
        }),
    )
    readonly_fields = ("created_at", "reviewed_at", "reviewed_by", "review_data")
