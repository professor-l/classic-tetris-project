import itertools
from django.db import transaction

from ..models import Tournament, TournamentMatch


BRACKET_COLORS = {
    1: "#e69138",
    2: "#6aa84f",
    3: "#c00000",
    4: "#3d85c6",
    5: "#42d4f4",
    6: "#f032e6",
    7: "#911eb4",
    8: "#c5ab00",
    9: "#d3aefd",
    10: "#9b5300",
    11: "#180033",
    12: "#4d9e65",
    13: "#808000",
    14: "#000075",
    15: "#469990",
    16: "#800000",
}

def tournament_size(player_count):
    n = 1
    while n < player_count:
        n *= 2
    return n


class BracketGenerator:
    class BracketGenerationError(Exception):
        pass

    def __init__(self, tournament):
        self.tournament = tournament

    @staticmethod
    def choose(tournament):
        if tournament.bracket_type == Tournament.BracketType.SINGLE_ELIMINATION:
            return SingleElimination(tournament)
        elif tournament.bracket_type == Tournament.BracketType.DOUBLE_ELIMINATION:
            return DoubleElimination(tournament)

    @transaction.atomic
    def generate(self):
        if self.tournament.matches.exists():
            raise BracketGenerationError("Tournament already has matches")
        self._generate_matches()

    def _generate_matches(self):
        pass


class SingleElimination(BracketGenerator):
    def _generate_matches(self):
        root = self._generate_match_data(1, 2)
        self._annotate_matches([root])
        self._create_match(root)

    # returns type, data
    def _create_match(self, match_data):
        if match_data["type"] == "seed":
            return TournamentMatch.PlayerSource.SEED, match_data["seed"]
        elif match_data["type"] == "match":
            match = TournamentMatch(
                tournament=self.tournament,
                match_number=match_data["match_number"],
                round_number=match_data["round_number"],
                color=match_data.get("color"),
            )

            match.source1_type, match.source1_data = self._create_match(match_data["children"][0])
            match.source2_type, match.source2_data = self._create_match(match_data["children"][1])
            match.save()

            return TournamentMatch.PlayerSource.MATCH_WINNER, match.match_number

    def _annotate_matches(self, matches):
        matches = [match for match in matches if match["type"] == "match"]
        if not matches:
            return 1, 1

        next_level = list(itertools.chain.from_iterable(
            match.get("children", []) for match in matches if match["type"] == "match"
        ))
        match_number, round_number = self._annotate_matches(next_level)

        for match in matches:
            match["match_number"] = match_number
            match["round_number"] = round_number
            match_number += 1

        return match_number, round_number + 1

    def _generate_match_data(self, highest_seed, player_count, depth = 0):
        seed1 = highest_seed
        seed2 = player_count + 1 - highest_seed

        if seed2 > self.tournament.seed_count:
            return { "type": "seed", "seed": seed1 }
        else:
            match1 = self._generate_match_data(seed1, player_count * 2, depth + 1)
            match2 = self._generate_match_data(seed2, player_count * 2, depth + 1)
            return {
                "type": "match",
                "children": [match1, match2],
                "color": self.match_color(highest_seed, depth)
            }

    def match_color(self, highest_seed, depth):
        if self.tournament.seed_count >= 64:
            if depth == 4:
                return BRACKET_COLORS[highest_seed]
        else:
            if depth == 2:
                return BRACKET_COLORS[highest_seed]


class DoubleElimination(BracketGenerator):
    def _generate_matches(self):
        winners_bracket = SingleElimination(self.tournament)._generate_match_data(1, 2)
        losers_bracket = self._generate_losers_bracket(winners_bracket, winners_bracket)

        match_number, round_number = self._annotate_matches([winners_bracket], [losers_bracket])
        root = {
            "type": "match",
            "children": [winners_bracket, losers_bracket],
            "match_number": match_number,
            "round_number": round_number
        }

        self._create_match(root)

    # returns type, data
    def _create_match(self, match_data):
        if match_data["type"] == "seed":
            return TournamentMatch.PlayerSource.SEED, match_data["seed"]
        elif match_data["type"] == "loser":
            return TournamentMatch.PlayerSource.MATCH_LOSER, match_data["source_match"]
        elif match_data["type"] == "match":
            match = TournamentMatch(
                tournament=self.tournament,
                match_number=match_data["match_number"],
                round_number=match_data["round_number"],
                color=match_data.get("color"),
            )

            match.source1_type, match.source1_data = self._create_match(match_data["children"][0])
            match.source2_type, match.source2_data = self._create_match(match_data["children"][1])
            match.save()

            return TournamentMatch.PlayerSource.MATCH_WINNER, match.match_number

    def _annotate_matches(self, winners_matches, losers_matches):
        winners_matches = [match for match in winners_matches if match["type"] == "match"]
        if not winners_matches:
            return 1, 1

        losers_matches = [match for match in losers_matches if match["type"] == "match"]
        losers_pre_matches = [match for match in itertools.chain.from_iterable(
            match.get("children", []) for match in losers_matches if match["type"] == "match"
        ) if match["type"] == "match"]

        next_winners_matches = list(itertools.chain.from_iterable(
            match.get("children", []) for match in winners_matches if match["type"] == "match"
        ))
        next_losers_matches = list(itertools.chain.from_iterable(
            match.get("children", []) for match in losers_pre_matches if match["type"] == "match"
        ))
        match_number, round_number = self._annotate_matches(next_winners_matches,
                                                            next_losers_matches)

        for match in losers_pre_matches:
            match["match_number"] = match_number
            match["round_number"] = round_number
            match_number += 1

        for match in winners_matches:
            match["match_number"] = match_number
            match["round_number"] = round_number
            match_number += 1

        for match in losers_matches:
            match["match_number"] = match_number
            match["round_number"] = round_number
            match_number += 1

        for match in (losers_pre_matches + losers_matches):
            self._resolve_sources(match, winners_matches)

        return match_number, round_number + 1

    def _resolve_sources(self, match, winners_matches):
        if match["type"] != "match":
            return

        for child in match["children"]:
            if child["type"] == "loser":
                child["source_match"] = child["source"]["match_number"]
                del child["source"]

    def _generate_losers_bracket(self, winners_bracket1, winners_bracket2):
        if winners_bracket1["type"] == "match":
            loser = { "type": "loser", "source": winners_bracket1}

            sub1 = None
            sub2 = None
            if winners_bracket1 == winners_bracket2:
                sub1 = self._generate_losers_bracket(winners_bracket1["children"][1],
                                                     winners_bracket1["children"][0])
                sub2 = self._generate_losers_bracket(winners_bracket1["children"][0],
                                                     winners_bracket1["children"][1])
                if self.bracket_depth(winners_bracket1) % 2 == 0:
                    sub1, sub2 = sub2, sub1
            elif winners_bracket1["type"] == "match" and winners_bracket2["type"] == "match":
                sub1 = self._generate_losers_bracket(winners_bracket2["children"][0],
                                                     winners_bracket1["children"][0])
                sub2 = self._generate_losers_bracket(winners_bracket2["children"][1],
                                                     winners_bracket1["children"][1])

            if sub1 and sub2:
                return { "type": "match", "children": [
                    loser,
                    { "type": "match", "children": [sub1, sub2] }
                ] }
            elif sub1 or sub2:
                return { "type": "match", "children": [loser, (sub1 or sub2)] }
            else:
                return loser
        else:
            return None

    def bracket_depth(self, match_data):
        if match_data["type"] == "match":
            return max(self.bracket_depth(child) for child in match_data["children"]) + 1
        else:
            return 0
