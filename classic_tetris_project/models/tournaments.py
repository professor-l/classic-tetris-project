from django.conf import settings
from django.db import models, transaction
from django.db.models import signals, Q
from django.urls import reverse
from django.utils.text import slugify
from colorfield.fields import ColorField
from furl import furl
from markdownx.models import MarkdownxField

from classic_tetris_project import tasks
from .users import User
from .events import Event
from .matches import Match
from .qualifiers import Qualifier


class Tournament(models.Model):
    name = models.CharField(
        max_length=64,
        blank=True,
        help_text="Full name of the tournament. Leave blank to automatically set to event name + short name."
    )
    short_name = models.CharField(
        max_length=64,
        help_text="Used in the context of an event, e.g. \"Masters Event\""
    )
    slug = models.SlugField(blank=True, db_index=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_index=False,
                              related_name="tournaments")
    order = models.PositiveIntegerField(default=0, help_text="Used to order tournaments for seeding")
    seed_count = models.IntegerField(help_text="Number of players to seed into this tournament")
    placeholders = models.JSONField(
        blank=True, default=dict,
        help_text="Reserves a seed that won't get automatically populated by a qualifier"
    )
    color = ColorField(default='#000000')
    public = models.BooleanField(
        default=False,
        help_text="Controls whether the tournament page is available to view"
    )
    restreamed = models.BooleanField(
        default=False,
        help_text="Determines whether this tournament's matches can be restreamed by default"
    )
    active = models.BooleanField(
        default=True,
        help_text="Controls whether this tournament's bracket should be updated on match completion"
    )
    details = MarkdownxField(
        blank=True,
        help_text="Details to show on the tournament page"
    )

    google_sheets_id = models.CharField(max_length=255, null=True, blank=True)
    google_sheets_range = models.CharField(max_length=255, null=True, blank=True)
    discord_emote_string = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event_id", "slug"],
                                    name="unique_event_slug")
        ]
        ordering = ["order"]

    def update_bracket(self):
        from ..util.tournament_sheet_updater import TournamentSheetUpdater
        for match in self.matches.filter(Q(player1__isnull=True) | Q(player2__isnull=True)):
            match.update_players()
        TournamentSheetUpdater(self).update()

    @staticmethod
    def before_save(sender, instance, **kwargs):
        if not instance.name:
            instance.name = f"{instance.event.name} {instance.short_name}"
        if not instance.slug:
            instance.slug = slugify(instance.short_name)

    def get_absolute_url(self, include_base=False):
        path = reverse("event:tournament:index", args=[self.event.slug, self.slug])
        if include_base:
            return furl(settings.BASE_URL, path=path).url
        else:
            return path

    def color_int(self):
        return int(self.color[1:], base=16)

    def __str__(self):
        return self.name

signals.pre_save.connect(Tournament.before_save, sender=Tournament)


class TournamentPlayer(models.Model):
    qualifier = models.OneToOneField(Qualifier, on_delete=models.RESTRICT,
                                     related_name="tournament_player", null=True, blank=True)
    user = models.ForeignKey(User, related_name="tournament_players",
                             on_delete=models.PROTECT,
                             db_index=False,
                             null=True, blank=True)
    tournament = models.ForeignKey(Tournament, related_name="tournament_players",
                                   on_delete=models.CASCADE,
                                   db_index=False)
    seed = models.IntegerField()
    name_override = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["tournament", "seed"])
        ]

    def display_name(self):
        if self.user:
            return self.user.display_name
        else:
            return self.name_override


    def __str__(self):
        return f"{self.user} ({self.tournament})"


class TournamentMatch(models.Model):
    class Meta:
        verbose_name_plural = "tournament matches"
        permissions = [
            ("restream", "Can schedule and report restreamed matches"),
        ]

    class PlayerSource(models.IntegerChoices):
        NONE = 1
        SEED = 2
        MATCH_WINNER = 3
        MATCH_LOSER = 4

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="matches")
    match = models.OneToOneField(Match, on_delete=models.PROTECT, null=True, blank=True,
                                 related_name="tournament_match")
    match_number = models.IntegerField()
    round_number = models.IntegerField(null=True, blank=True)
    restreamed = models.BooleanField(default=False)

    source1_type = models.IntegerField(choices=PlayerSource.choices)
    source1_data = models.IntegerField(null=True, blank=True)
    source2_type = models.IntegerField(choices=PlayerSource.choices)
    source2_data = models.IntegerField(null=True, blank=True)

    player1 = models.ForeignKey(TournamentPlayer, on_delete=models.RESTRICT, related_name="+",
                                null=True, blank=True)
    player2 = models.ForeignKey(TournamentPlayer, on_delete=models.RESTRICT, related_name="+",
                                null=True, blank=True)
    winner = models.ForeignKey(TournamentPlayer, on_delete=models.RESTRICT, related_name="+",
                               null=True, blank=True)
    loser = models.ForeignKey(TournamentPlayer, on_delete=models.RESTRICT, related_name="+",
                              null=True, blank=True)

    def update_players(self):
        if not self.player1:
            self.player1 = self.player_from_source(self.source1_type, self.source1_data)
        if not self.player2:
            self.player2 = self.player_from_source(self.source2_type, self.source2_data)
        self.save()

    def player_from_source(self, source_type, source_data):
        if source_type == TournamentMatch.PlayerSource.NONE:
            return None
        elif source_type == TournamentMatch.PlayerSource.SEED:
            return self.tournament.tournament_players.filter(seed=source_data).first()
        elif source_type == TournamentMatch.PlayerSource.MATCH_WINNER:
            match = self.tournament.matches.filter(match_number=source_data).first()
            if match:
                return match.winner
        elif source_type == TournamentMatch.PlayerSource.MATCH_LOSER:
            match = self.tournament.matches.filter(match_number=source_data).first()
            if match:
                return match.loser

    def is_playable(self):
        return bool(self.player1 and self.player1.user and
                    self.player2 and self.player2.user and
                    not self.winner)

    def is_scheduled(self):
        return bool(self.match and self.match.start_date)

    def is_complete(self):
        return bool(self.winner)

    def get_or_create_match(self):
        if not self.match:
            self.match = Match.objects.create(player1=self.player1.user, player2=self.player2.user)
            self.save()
        return self.match

    def update_from_match(self):
        if self.match:
            if self.match.wins1 > self.match.wins2:
                self.winner = self.player1
                self.loser = self.player2
            elif self.match.wins2 > self.match.wins1:
                self.winner = self.player2
                self.loser = self.player1
            self.save()
            if self.tournament.active:
                transaction.on_commit(
                    lambda: tasks.update_tournament_bracket.delay(self.tournament.id))

    def get_absolute_url(self, include_base=False):
        path = reverse("event:tournament:match:index",
                       args=[self.tournament.event.slug, self.tournament.slug, self.match_number])
        if include_base:
            return furl(settings.BASE_URL, path=path).url
        else:
            return path

    def __str__(self):
        return f"{self.tournament} Match {self.match_number}"

    @staticmethod
    def before_save(sender, instance, **kwargs):
        if not instance.id:
            instance.restreamed = instance.tournament.restreamed

signals.pre_save.connect(TournamentMatch.before_save, sender=TournamentMatch)
