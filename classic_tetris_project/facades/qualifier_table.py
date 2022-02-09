import itertools


class QualifierTable:
    def __init__(self, event):
        self.event = event
        self.tournaments = list(self.event.tournaments.order_by("order"))
        self.withheld_qualifier_ids = []
        for tournament in self.tournaments:
            if tournament.placeholders:
                for placeholder in tournament.placeholders.values():
                    if "qualifier" in placeholder:
                        self.withheld_qualifier_ids.append(int(placeholder["qualifier"]))

        self.qualifiers = list(self.event.qualifiers.public()
                               .exclude(id__in=self.withheld_qualifier_ids)
                               .order_by("-qualifying_score")
                               .prefetch_related("user__twitch_user"))

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
                qualifier = self.qualifiers[offset]

                if str(seed) in tournament.placeholders:
                    placeholder = tournament.placeholders[str(seed)]
                    qualifier = (self.event.qualifiers.get(id=int(placeholder["qualifier"]))
                                 if "qualifier" in placeholder else None)
                    qualifier_rows.append({
                        "seed": seed,
                        "placeholder": placeholder["name"],
                        "qualifier": qualifier
                    })
                else:
                    qualifier_rows.append({
                        "seed": seed,
                        "qualifier": qualifier
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
