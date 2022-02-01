from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import Http404
from django.shortcuts import redirect, render

from classic_tetris_project.facades.tournament_match_display import TournamentMatchDisplay
from classic_tetris_project.models import TournamentMatch
from classic_tetris_project.util import lazy
from .tournaments import TournamentView


class MatchView(TournamentView):
    @lazy
    def match(self):
        try:
            return self.tournament.matches.get(match_number=int(self.kwargs["match_number"]))
        except TournamentMatch.DoesNotExist:
            raise Http404()

    @lazy
    def match_display(self):
        return TournamentMatchDisplay(self.match, self.current_user)


class IndexView(MatchView):
    def get(self, request, event_slug, tournament_slug, match_number):
        return render(request, "tournament_match/show.haml", {
            "match": self.match,
            "match_display": self.match_display,
            "tournament": self.tournament,
        })


class ScheduleView(UserPassesTestMixin, MatchView):
    def get(self, request, event_slug, tournament_slug, match_number):
        from ..forms import tournament_match as match_forms
        return render(request, "tournament_match/schedule.haml", {
            "match": self.match,
            "match_display": self.match_display,
            "tournament": self.tournament,
            "form": match_forms.ScheduleForm(initial={
                "channel": self.own_twitch_channel_id(),
            }, instance=self.match.match),
        })

    def post(self, request, event_slug, tournament_slug, match_number):
        from ..forms import tournament_match as match_forms
        form = match_forms.ScheduleForm(request.POST, instance=self.match.get_or_create_match())
        if form.is_valid():
            form.save()
            return redirect(self.match.get_absolute_url())
        else:
            return render(request, "tournament_match/schedule.haml", {
                "match": self.match,
                "match_display": self.match_display,
                "tournament": self.tournament,
                "form": form
            })

    def delete(self, request, event_slug, tournament_slug, match_number):
        if self.match.match:
            self.match.match.start_date = None
            self.match.match.channel = None
            self.match.match.save()
        return redirect(self.match.get_absolute_url())

    def test_func(self):
        return self.match_display.can_restream()

    def own_twitch_channel_id(self):
        if (self.current_user and self.current_user.twitch_user and
                self.current_user.twitch_user.channel):
            return self.current_user.twitch_user.channel.pk


class ReportView(UserPassesTestMixin, MatchView):
    def get(self, request, event_slug, tournament_slug, match_number):
        from ..forms import tournament_match as match_forms
        return render(request, "tournament_match/report.haml", {
            "match": self.match,
            "match_display": self.match_display,
            "tournament": self.tournament,
            "form": match_forms.ReportForm(instance=self.match.get_or_create_match()),
        })

    def post(self, request, event_slug, tournament_slug, match_number):
        from ..forms import tournament_match as match_forms
        form = match_forms.ReportForm(request.POST, instance=self.match.get_or_create_match())
        if form.is_valid():
            form.save(self.current_user)
            return redirect(self.match.get_absolute_url())
        else:
            return render(request, "tournament_match/report.haml", {
                "match": self.match,
                "match_display": self.match_display,
                "tournament": self.tournament,
                "form": form
            })

    def test_func(self):
        return self.match_display.can_restream()
