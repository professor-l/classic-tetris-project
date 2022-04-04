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
        self.color_left = 5
        self.color_right = 5

    def add_left(self, node):
        if node:
            self.left = node
            node.parent = self

    def add_right(self, node):
        if node:
            self.right = node
            node.parent = self

    def color_all(self, color_index):
        self.color_left = color_index
        self.color_right = color_index

        if self.left:
            self.left.color_all(color_index)

        if self.right:
            self.right.color_all(color_index)

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

class TournamentBracket:
    def __init__(self, tournament, user):
        self.tournament = tournament
        self.user = user

    def build(self):
        bracket_nodes = { match.match_number: MatchNode(match, self.user) for match in
                         self.tournament.all_matches() }

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
        semi_left.color_left = 1
        semi_left.color_right = 2
        semi_right.color_left = 3
        semi_right.color_right = 4

        semi_left.left.color_all(1)
        semi_left.right.color_all(2)
        semi_right.left.color_all(3)
        semi_right.right.color_all(4)

    def display_rounds(self):
        rounds = []
        for round_number in range(1, self.root.match.round_number + 1):
            rounds.append({
                "label": self._round_label(round_number),
                "number": round_number,
                "matches": self.root.get_nodes_at_level(self.root.match.round_number - round_number)
            })
        return rounds

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
