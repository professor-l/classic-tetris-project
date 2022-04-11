from ..facades.tournament_match_display import TournamentMatchDisplay
from .google_sheets import GoogleSheetsService


MATCH_NUMBER = "match number"
ROUND_NUMBER = "round number"
PLAYER_1 = "player 1"
PLAYER_1_SEED = "player 1 seed"
PLAYER_1_WINS = "player 1 wins"
PLAYER_2 = "player 2"
PLAYER_2_SEED = "player 2 seed"
PLAYER_2_WINS = "player 2 wins"
WINNER = "winner"
LOSER = "loser"
TIME = "time"
CHANNEL = "channel"
VOD = "vod"
MATCH_URL = "match url"

HEADERS = [
    MATCH_NUMBER, ROUND_NUMBER,
    PLAYER_1, PLAYER_1_SEED, PLAYER_1_WINS,
    PLAYER_2, PLAYER_2_SEED, PLAYER_2_WINS,
    WINNER, LOSER,
    TIME, CHANNEL, VOD, MATCH_URL,
]

class TournamentSheetUpdateError(Exception):
    pass

class TournamentSheetUpdater:
    def __init__(self, tournament):
        self.tournament = tournament
        self.matches = list(tournament.matches.order_by("match_number"))

    def update(self):
        if self.tournament.google_sheets_id and self.tournament.google_sheets_range:
            sheets = GoogleSheetsService()
            sheets.update(
                self.tournament.google_sheets_id,
                self.tournament.google_sheets_range,
                self.tournament_data()
            )

    def tournament_data(self):
        data = []
        data.append(HEADERS)
        for match in self.tournament.matches.order_by("match_number"):
            row = self.match_data(match)
            data.append([row[header] for header in HEADERS])
        data.append(["DO NOT EDIT, THIS SHEET IS AUTOMATICALLY GENERATED"])
        return data

    def match_data(self, match):
        match_time = match.match.start_date or match.match.ended_at if match.match else None
        return {
            MATCH_NUMBER: match.match_number,
            ROUND_NUMBER: match.round_number,
            PLAYER_1: match.player1.user.display_name if match.player1 and match.player1.user else "",
            PLAYER_1_SEED: match.player1.seed if match.player1 else "",
            PLAYER_1_WINS: match.match.wins1 if match.match and match.match.ended_at else "",
            PLAYER_2: match.player2.user.display_name if match.player2 and match.player2.user else "",
            PLAYER_2_SEED: match.player2.seed if match.player2 else "",
            PLAYER_2_WINS: match.match.wins2 if match.match and match.match.ended_at else "",
            WINNER: match.winner.display_name() if match.winner else "",
            LOSER: match.loser.display_name() if match.loser else "",
            TIME: match_time.isoformat() if match_time else "",
            CHANNEL: match.match.channel.name if match.match and match.match.channel else "",
            VOD: match.match.vod if match.match else "",
            MATCH_URL: match.get_absolute_url(include_base=True),
        }
