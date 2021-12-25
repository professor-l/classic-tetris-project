import itertools


class QualifierTable:
    def __init__(self, event):
        self.event = event
        self.tournaments = list(self.event.tournaments.order_by("order"))
        self.qualifiers = list(self.event.qualifiers.public().order_by("-qualifying_score"))

    def groups(self):
        groups_data = []
        offset = 0
        qualifier_count = len(self.qualifiers)
        for tournament in self.tournaments + [None]:
            if offset >= qualifier_count:
                break
            group_data, offset = self.group_data(tournament, offset)
            groups_data.append(group_data)
        return groups_data

    def group_data(self, tournament, offset):
        if tournament:
            qualifier_rows = []
            for seed in range(1, tournament.seed_count + 1):
                if offset >= len(self.qualifiers):
                    break
                if str(seed) in tournament.placeholders:
                    qualifier_rows.append({
                        "seed": seed,
                        "placeholder": tournament.placeholders[str(seed)]
                    })
                else:
                    qualifier_rows.append({
                        "seed": seed,
                        "qualifier": self.qualifiers[offset]
                    })
                    offset += 1
            return {
                "tournament": tournament,
                "qualifier_rows": qualifier_rows,
            }, offset
        else:
            return {
                "qualifier_rows": [{ "qualifier": qualifier } for qualifier in self.qualifiers[offset:]]
            }, len(self.qualifiers)
