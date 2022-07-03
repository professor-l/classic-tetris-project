import json
from django.core.cache import cache
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from classic_tetris_project.models import Tournament
from classic_tetris_project.facades.tournament_match_display import TournamentMatchDisplay
from classic_tetris_project.facades.tournament_bracket import TournamentBracket
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
        if not (self.tournament.public or (self.current_user and
                                           self.current_user.permissions.change_tournament())):
            raise Http404()

        all_players = list(self.tournament.tournament_players.order_by("seed")
                           .prefetch_related("user__twitch_user", "qualifier"))
        all_matches = [TournamentMatchDisplay(match, self.current_user)
                       for match in self.tournament.all_matches()]
        playable_matches = [match_display for match_display in all_matches
                            if match_display.tournament_match.is_playable()]

        bracket = TournamentBracket(self.tournament, self.current_user)
        bracket.build()

        return render(request, "tournament/index.haml", {
            "tournament": self.tournament,
            "tournament_players": all_players,
            "tournament_matches": all_matches,
            "playable_matches": playable_matches,
            "bracket": bracket,
        })

BRACKET_OPTIONS = {
    "scaled",
    "fitToWindow",
    "width",
    "height",
    "depth",
    "root",
    "showBorder",
    "autoRefresh",
    "embed",
}

class BracketView(TournamentView):
    @xframe_options_exempt
    def get(self, request, event_slug, tournament_slug):
        if not (self.tournament.public or (self.current_user and
                                           self.current_user.permissions.change_tournament())):
            raise Http404()

        bracket = TournamentBracket(self.tournament, self.current_user)
        bracket.build()

        bracket_options = {
            option: request.GET.get(option)
            for option in BRACKET_OPTIONS
            if option in request.GET
        }

        if not bracket.root:
            raise Http404()

        return render(request, "tournament/bracket.haml", {
            "tournament": self.tournament,
            "bracket_props": bracket.react_props(bracket_options),
            "embed": request.GET.get("embed") == "true",
        })

class BracketJsonView(TournamentView):
    CACHE_TIMEOUT = 60

    def get(self, request, event_slug, tournament_slug):
        if not (self.tournament.public or (self.current_user and
                                           self.current_user.permissions.change_tournament())):
            raise Http404()

        return JsonResponse(self.get_data())

    def get_data(self):
        data = cache.get(self.cache_key)
        if data:
            try:
                data = json.loads(data)
                if self.timestamp is None or data['ts'] > self.timestamp:
                    return data
                else:
                    # client has the same or newer data
                    return {}
            except json.JSONDecodeError:
                return self.fetch_data()
        else:
            return self.fetch_data()

    def fetch_data(self):
        bracket = TournamentBracket(self.tournament, None)
        bracket.build()
        data = bracket.match_data()
        cache.set(self.cache_key, json.dumps(data), timeout=BracketJsonView.CACHE_TIMEOUT)
        return data

    @lazy
    def cache_key(self):
        return f"tournament_json.{self.tournament.id}"

    @lazy
    def timestamp(self):
        ts = self.request.GET.get("ts")
        if ts:
            try:
                return int(ts)
            except ValueError:
                return None
        else:
            return None
