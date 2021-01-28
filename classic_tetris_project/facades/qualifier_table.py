import itertools


class QualifierTable:
    # This is hard-coded until tournament seeding is built
    QUALIFYING_GROUPS = [
        {
            "name": "Masters",
            "color": "#37761D",
            "size": 15,
            "placeholders": ["CC Winner"],
        },
        {
            "name": "Challengers",
            "color": "#E69138",
            "size": 16,
        },
        {
            "name": "Futures",
            "color": "#741C47",
            "size": 32,
        },
        {
            "name": "Community T1",
            "color": "#6FA8DC",
            "size": 32,
        },
        {
            "name": "Community T2",
            "color": "#3E85C6",
            "size": 32,
        },
        {
            "name": "Community T3",
            "color": "#0C5394",
            "size": 32,
        },
        {
            "name": "Community T4",
            "color": "#F0C233",
            "size": 32,
        },
        {
            "name": "Community T5",
            "color": "#FFE599",
            "size": 32,
        },
    ]

    def __init__(self, event):
        self.event = event
        self.qualifiers = self.event.qualifiers.filter(approved=True).order_by("-qualifying_score")

    def groups(self):
        groups_data = []
        offset = 0
        qualifier_count = len(self.qualifiers)
        for group in self.QUALIFYING_GROUPS:
            if offset >= qualifier_count:
                break
            groups_data.append(self.group_data(group, offset))
            offset += group["size"]
        return groups_data

    def group_data(self, group, offset):
        qualifier_rows = []
        for qualifier, _ in itertools.zip_longest(self.qualifiers[offset:offset+group["size"]],
                                                  range(group["size"])):
            if qualifier:
                qualifier_rows.append({ "qualifier": qualifier })
            else:
                qualifier_rows.append(None)
        if "placeholders" in group:
            for placeholder_name in group["placeholders"]:
                qualifier_rows.append({ "placeholder": placeholder_name })
        return {
            "name": group["name"],
            "color": group["color"],
            "qualifier_rows": qualifier_rows,
        }
