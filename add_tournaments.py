from classic_tetris_project.models import *

def add_tournaments(event):
    for i, tournament_data in enumerate([
            {
                "name": "Masters Event",
                "color": "#37761D",
                "size": 16,
                "placeholders": {"16":"CC Winner"},
            },
            {
                "name": "Challengers Circuit",
                "color": "#E69138",
                "size": 16,
                "placeholders": {},
            },
            {
                "name": "Futures Circuit",
                "color": "#741C47",
                "size": 32,
                "placeholders": {},
            },
            {
                "name": "Community T1",
                "color": "#6FA8DC",
                "size": 32,
                "placeholders": {},
            },
            {
                "name": "Community T2",
                "color": "#3E85C6",
                "size": 32,
                "placeholders": {},
            },
            {
                "name": "Community T3",
                "color": "#0C5394",
                "size": 32,
                "placeholders": {},
            },
            {
                "name": "Community T4",
                "color": "#F0C233",
                "size": 32,
                "placeholders": {},
            },
            {
                "name": "Community T5",
                "color": "#FFE599",
                "size": 32,
                "placeholders": {},
            },
    ]):
        Tournament.objects.create(
            event=event,
            short_name=tournament_data["name"],
            order=i,
            seed_count=tournament_data["size"],
            placeholders=tournament_data["placeholders"],
            color=tournament_data["color"],
        )
