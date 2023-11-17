import time
from django.urls import reverse

from classic_tetris_project.facades.tournament_match_display import TournamentMatchDisplay
from classic_tetris_project.models import TournamentMatch
from classic_tetris_project.util import memoize


class MatchNode:
    def __init__(self, match, viewing_user):
        self.left = None
        self.right = None
        self.parent = None
        self.match = match
        self.viewing_user = viewing_user

    def add_left(self, node):
        if node:
            self.left = node
            node.parent = self

    def add_right(self, node):
        if node:
            self.right = node
            node.parent = self

    def get_nodes_at_level(self, level):
        if level == 0:
            return [self]
        else:
            nodes = []

            if self.left:
                nodes.extend(self.left.get_nodes_at_level(level - 1))
            else:
                nodes.extend([None] * (2 ** (level - 1)))

            if self.right:
                nodes.extend(self.right.get_nodes_at_level(level - 1))
            else:
                nodes.extend([None] * (2 ** (level - 1)))
            return nodes

    @memoize
    def display(self):
        return TournamentMatchDisplay(self.match, self.viewing_user)

    def match_data(self):
        return {
            "label": f"Match {self.match.match_number}",
            "url": self.match.get_absolute_url(),
            "matchNumber": self.match.match_number,
            "color": self.match.color,
            "left": {
                "playerName": self.display().player1_display_name(),
                "playerSeed": self.match.player1 and self.match.player1.seed,
                "url": self.match.player1 and self.match.player1.get_absolute_url(),
                "winner": self.display().player1_winner(),
                "child": self.left and self.left.match_data(),
            },
            "right": {
                "playerName": self.display().player2_display_name(),
                "playerSeed": self.match.player2 and self.match.player2.seed,
                "url": self.match.player2 and self.match.player2.get_absolute_url(),
                "winner": self.display().player2_winner(),
                "child": self.right and self.right.match_data(),
            },
        }

class TournamentBracket:
    def __init__(self, tournament, user):
        self.tournament = tournament
        self.user = user
        self.root = None

    def build(self):
        bracket_nodes = { match.match_number: MatchNode(match, self.user) for match in
                         self.tournament.all_matches() }

        if not bracket_nodes:
            return 

        for node in bracket_nodes.values():
            left_source = node.match.source1_type
            left_data = node.match.source1_data
            right_source = node.match.source2_type
            right_data = node.match.source2_data

            if left_source == TournamentMatch.PlayerSource.MATCH_WINNER:
                node.add_left(bracket_nodes[left_data])

            if right_source == TournamentMatch.PlayerSource.MATCH_WINNER:
                node.add_right(bracket_nodes[right_data])
        self.root = next(node for node in bracket_nodes.values() if node.parent is None)
        semi_left = self.root.left
        semi_right = self.root.right

    def display_rounds(self):
        rounds = []
        for round_number in range(1, self.root.match.round_number + 1):
            rounds.append({
                "label": self._round_label(round_number),
                "number": round_number,
                "matches": self.root.get_nodes_at_level(self.root.match.round_number - round_number)
            })
        return rounds

    def react_props(self, options={}):
        return {
            **self.match_data(),
            "refreshUrl": self.tournament.get_bracket_url(include_base=True, json=True),
            "bracketUrl": self.tournament.get_bracket_url(include_base=True),
            "customBracketColor": self.tournament.bracket_color,
            "useCustomFont": self.tournament.event.use_custom_font,
            **options
        }

    def embed_props(self, options={}):
        return self.react_props({ **options, "embed": True })

    def match_data(self):
        return {
            "matches": self.root.match_data(),
            "ts": int(time.time()),
        }

    @memoize
    def has_feed_ins(self):
        player_count = self.tournament.tournament_players.count()
        return not (player_count & (player_count - 1) == 0) and player_count != 0

    def _round_label(self, round_number):
        if round_number == self.root.match.round_number:
            return "Finals"
        elif round_number == self.root.match.round_number - 1:
            return "Semifinals"
        else:
            return f"Round {round_number}"
