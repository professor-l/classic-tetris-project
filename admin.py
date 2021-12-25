from django import forms
from django.conf import settings
from django.contrib import admin, auth, messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import text, timezone
from django_object_actions import DjangoObjectActions
from markdownx.admin import MarkdownxModelAdmin
from adminsortable2.admin import SortableInlineAdminMixin

from ..models import *


class DiscordUserInline(admin.StackedInline):
    model = DiscordUser

class TwitchUserInline(admin.StackedInline):
    model = TwitchUser

class WebsiteUserInline(admin.StackedInline):
    model = WebsiteUser
    autocomplete_fields = ("auth_user",)

@admin.register(User)
class UserAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [DiscordUserInline, TwitchUserInline, WebsiteUserInline]
    search_fields = ("preferred_name", "discord_user__username", "twitch_user__username")

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
    autocomplete_fields = ("user",)
    search_fields = ("username",)

@admin.register(TwitchUser)
class TwitchUserAdmin(admin.ModelAdmin):
    list_display = ("username", "twitch_id")
    autocomplete_fields = ("user",)
    search_fields = ("username",)


class GameInline(admin.TabularInline):
    model = Game
    autocomplete_fields = ("winner",)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    inlines = [GameInline]
    list_display = ('__str__', 'player1', 'wins1', 'player2', 'wins2', 'channel', 'ended_at')
    autocomplete_fields = ("player1", "player2", "channel")


class CustomCommandInline(admin.TabularInline):
    model = CustomCommand

@admin.register(TwitchChannel)
class TwitchChannelAdmin(admin.ModelAdmin):
    inlines = [CustomCommandInline]
    list_display = ("twitch_user", "connected")
    autocomplete_fields = ("twitch_user",)
    search_fields = ("twitch_user__username",)


@admin.register(Page)
class PageAdmin(MarkdownxModelAdmin):
    prepopulated_fields = { "slug": ("title",) }
    list_display = ("title", "slug", "public", "updated_at")


class TournamentInline(SortableInlineAdminMixin, admin.StackedInline):
    class TournamentForm(forms.ModelForm):
        # Duplicates logic in Tournament#before_save, required for formset validation
        def clean_slug(self):
            if self.cleaned_data["slug"]:
                return self.cleaned_data["slug"]
            else:
                return text.slugify(self.cleaned_data["short_name"])

    model = Tournament
    form = TournamentForm
    extra = 0
    show_change_link = True

@admin.register(Event)
class EventAdmin(DjangoObjectActions, MarkdownxModelAdmin):
    inlines = [TournamentInline]
    prepopulated_fields = { "slug": ("name",) }
    list_display = ("name", "qualifying_open")

    def seed_tournaments(self, request, obj):
        obj.seed_tournaments()
        messages.success(request, "Tournaments seeded")

    change_actions = ("seed_tournaments",)

@admin.register(Qualifier)
class QualifierAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "qualifying_score", "status_tag", "reviewed_at")
    list_filter = ("approved",)

    fieldsets = (
        ("Qualifier Data", {
            "fields": ("user", "event", "qualifying_type", "qualifying_score", "qualifying_data",
                       "vod", "auth_word", "details", "submitted", "withdrawn", "created_at",
                       "submitted_at"),
        }),
        ("Moderator Data", {
            "fields": ("approved", "reviewed_by", "reviewed_at", "review_data"),
            "description": ("Qualifiers can be reviewed from <a href='/review_qualifiers/'>this "
                            "page</a>. Change Approved to \"Unknown\" to allow a qualifier to be "
                            "reviewed again.")
        }),
    )
    readonly_fields = ("user", "event", "qualifying_type", "created_at", "submitted_at",
                       "reviewed_at", "reviewed_by", "review_data")

class TournamentPlayerInline(admin.TabularInline):
    model = TournamentPlayer
    extra = 0
    show_change_link = True

    raw_id_fields = ("qualifier",)
    autocomplete_fields = ("user",)

class TournamentMatchInline(admin.TabularInline):
    model = TournamentMatch
    extra = 0
    show_change_link = True

    readonly_fields = ("player1", "player2", "winner", "loser", "match")


from django.urls import path
from classic_tetris_project.util import bracket_generator

@admin.register(Tournament)
class TournamentAdmin(DjangoObjectActions, admin.ModelAdmin):
    inlines = [TournamentPlayerInline, TournamentMatchInline]

    change_actions = ("generate_matches", "update_bracket")

    def generate_matches(self, request, obj):
        # TODO intermediate page to select bracket type
        generator = bracket_generator.SingleElimination(obj)
        try:
            generator.generate()
            messages.success(request, "Matches added")
        except bracket_generator.BracketGenerationError as e:
            messages.error(request, str(e))

    def update_bracket(self, request, obj):
        obj.update_bracket()
        messages.success(request, "Bracket updated")

@admin.register(TournamentMatch)
class TournamentMatchAdmin(admin.ModelAdmin):
    list_display = ("match_number", "tournament", "player1", "player2")
    list_filter = ("tournament",)

    raw_id_fields = ("match", "player1", "player2", "winner", "loser")

@admin.register(TournamentPlayer)
class TournamentPlayerAdmin(admin.ModelAdmin):
    list_display = ("user", "tournament", "seed")
    list_filter = ("tournament",)

    raw_id_fields = ("qualifier",)
    autocomplete_fields = ("user",)
