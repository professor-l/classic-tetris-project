import itertools
from django.db import transaction

from ..models import TournamentMatch


class BracketGenerationError(Exception):
    pass

def tournament_size(player_count):
    n = 1
    while n < player_count:
        n *= 2
    return n


class BracketGenerator:
    def __init__(self, tournament):
        self.tournament = tournament

    @transaction.atomic
    def generate(self):
        if self.tournament.matches.exists():
            raise BracketGenerationError("Tournament already has matches")
        self.generate_matches()

    def generate_matches(self):
        pass


class SingleElimination(BracketGenerator):
    def generate_matches(self):
        root = self.generate_match(1, 2)
        self.annotate_matches([root])
        self.create_match(root)

    # returns type, data
    def create_match(self, match_data):
        if match_data["type"] == "seed":
            return TournamentMatch.PlayerSource.SEED, match_data["seed"]
        elif match_data["type"] == "match":
            match = TournamentMatch(
                tournament=self.tournament,
                match_number=match_data["match_number"],
                round_number=match_data["round_number"]
            )

            match.source1_type, match.source1_data = self.create_match(match_data["children"][0])
            match.source2_type, match.source2_data = self.create_match(match_data["children"][1])
            match.save()

            return TournamentMatch.PlayerSource.MATCH_WINNER, match.match_number

    def annotate_matches(self, matches):
        matches = [match for match in matches if match["type"] == "match"]
        if not matches:
            return 1, 1

        next_level = list(itertools.chain.from_iterable(
            match.get("children", []) for match in matches if match["type"] == "match"
        ))
        match_number, round_number = self.annotate_matches(next_level)

        for match in matches:
            match["match_number"] = match_number
            match["round_number"] = round_number
            match_number += 1

        return match_number, round_number + 1

    def generate_match(self, highest_seed, player_count):
        seed1 = highest_seed
        seed2 = player_count + 1 - highest_seed

        if seed2 > self.tournament.seed_count:
            return { "type": "seed", "seed": seed1 }
        else:
            match1 = self.generate_match(seed1, player_count * 2)
            match2 = self.generate_match(seed2, player_count * 2)
            return { "type": "match", "children": [match1, match2] }
