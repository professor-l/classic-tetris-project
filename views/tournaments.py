from django.http import Http404
from django.shortcuts import render

from classic_tetris_project.models import Tournament, TournamentMatch
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


class MatchNode:
    def __init__(self, match):
        self.left = None
        self.right = None
        self.match = match
        self.color_left = 5
        self.color_right = 5

    def color_all(self, color_index):
        self.color_left = color_index
        self.color_right = color_index

        if self.left:
            self.left.color_all(color_index)

        if self.right:
            self.right.color_all(color_index)

    def get_nodes_at_round(self, round_num):
        nodes = [self]
        for i in range(round_num - 1):
            children = []
            for node in nodes:
                children.extend([node.left, node.right])
            nodes = children
        return nodes


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

        bracket_nodes = []
        for match in all_matches:
            node = MatchNode(match)
            bracket_nodes.append(node)

        for node in reversed(bracket_nodes):
            left_source = node.match.tournament_match.source1_type
            left_data = node.match.tournament_match.source1_data
            right_source = node.match.tournament_match.source2_type
            right_data = node.match.tournament_match.source2_data

            if left_source == TournamentMatch.PlayerSource.MATCH_WINNER:
                node.left = bracket_nodes[left_data - 1]

            if right_source == TournamentMatch.PlayerSource.MATCH_WINNER:
                node.right = bracket_nodes[right_data - 1]

        root_bracket_node = bracket_nodes[-1]
        semi_left = root_bracket_node.left
        semi_right = root_bracket_node.right
        semi_left.color_left = 1
        semi_left.color_right = 2
        semi_right.color_left = 3
        semi_right.color_right = 4

        semi_left.left.color_all(1)
        semi_left.right.color_all(2)
        semi_right.left.color_all(3)
        semi_right.right.color_all(4)

        bracket_matches = []

        for i in range(root_bracket_node.match.tournament_match.round_number, 0, -1):
            matches_at_round = root_bracket_node.get_nodes_at_round(i)
            bracket_matches.append(matches_at_round)

        player_count = len(all_players)
        has_feed_ins = not (player_count & (player_count - 1) == 0) and player_count != 0

        return render(request, "tournament/index.haml", {
            "tournament": self.tournament,
            "tournament_players": all_players,
            "tournament_matches": all_matches,
            "playable_matches": playable_matches,
            "bracket_matches": bracket_matches,
            "root_bracket_node": bracket_nodes[-1],
            "has_feed_ins": has_feed_ins
        })
