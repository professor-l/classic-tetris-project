from django.http import Http404
from django.shortcuts import render

from classic_tetris_project.models import Tournament
from classic_tetris_project.util import lazy
from .events import EventView


class TournamentView(EventView):
    @lazy
    def tournament(self):
        try:
            return self.event.tournaments.get(slug=self.kwargs["tournament_slug"])
        except Tournament.DoesNotExist:
            raise Http404()


class IndexView(TournamentView):
    def get(self, request, event_slug, tournament_slug):
        if not self.tournament.public:
            raise Http404()

        return render(request, "tournament/index.html", {
            "tournament": self.tournament,
            "tournament_players": list(self.tournament.tournament_players.all()),
            "tournament_matches": self.tournament.matches.order_by("match_number"),
        })
