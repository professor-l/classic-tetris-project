from django.http import Http404
from django.shortcuts import render

from classic_tetris_project.models import Tournament
from classic_tetris_project.facades.tournament_match_display import TournamentMatchDisplay
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

        all_players = list(self.tournament.tournament_players.order_by("seed")
                           .prefetch_related("user__twitch_user", "qualifier"))
        all_matches = [TournamentMatchDisplay(match, self.current_user) for match in
                       self.tournament.matches.order_by("match_number")
                       .prefetch_related("player1__user__twitch_user", "player2__user__twitch_user",
                                         "winner", "match")]
        playable_matches = [match_display for match_display in all_matches
                            if match_display.tournament_match.is_playable()]

        bracket_matches = []
        all_matches_copy = all_matches.copy()
        player_count = len(all_players)

        while player_count > 1:
            player_count //= 2
            bracket_matches.append(TournamentMatchDisplay.generate_round(player_count, all_matches_copy))

        return render(request, "tournament/index.haml", {
            "tournament": self.tournament,
            "tournament_players": all_players,
            "tournament_matches": all_matches,
            "playable_matches": playable_matches,
            "bracket_matches": bracket_matches,
        })
