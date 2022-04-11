import pytz
import json
from collections import defaultdict

from django.conf import settings
from django.utils import timezone

from classic_tetris_project.models import Match, Game
from .google_sheets import GoogleSheetsService

spreadsheet_id = "1l-dWUEQyeRobxMYObAucxIeRIpC0VsXCYuOHU5mXTXg"
sheet_range = "all matches test!A1:Z"

class MatchSheetReporter:
    def __init__(self):
        self.sheets_service = GoogleSheetsService()
        self.spreadsheet_id = settings.ENV("MATCH_REPORTING_SPREADSHEET_ID")
        self.sheet_range = settings.ENV("MATCH_REPORTING_SHEET_RANGE")

    def sync_all(self):
        match_count = 0
        for matches in self.unsynced_match_batches():
            game_data = self.game_data(matches)
            match_data = [
                [
                    match.id,
                    match.player1.twitch_user.username,
                    match.player2.twitch_user.username,
                    match.wins1,
                    match.wins2,
                    (match.start_date.astimezone(pytz.utc).isoformat() if
                     match.start_date else None),
                    match.ended_at.astimezone(pytz.utc).isoformat(),
                    (match.channel.twitch_user.username if match.channel else None),
                    (match.tournament_match.tournament.name
                     if hasattr(match, "tournament_match") else None),
                    (json.dumps(game_data[match.id]) if game_data[match.id] else None),
                ]
                for match in matches
            ]
            now = timezone.now()
            self.sheets_service.append(self.spreadsheet_id, self.sheet_range, match_data)
            Match.objects.filter(id__in=[match.id for match in matches]).update(synced_at=now)
            match_count += len(matches)

        return match_count

    def unsynced_match_batches(self, batch_size=100):
        min_id = 0
        scope = Match.objects.filter(synced_at__isnull=True, ended_at__isnull=False, tournament_match__isnull=False).order_by("id")

        while True:
            matches = list(scope.filter(id__gt=min_id).prefetch_related(
                "player1__twitch_user",
                "player2__twitch_user",
                "channel__twitch_user",
                "tournament_match__tournament",
            )[:batch_size])
            yield matches

            if len(matches) < batch_size:
                break

            min_id = matches[-1].id

    def game_data(self, matches):
        game_data = {}
        all_games = Game.objects.filter(
            match_id__in=[match.id for match in matches]
        ).prefetch_related("winner__twitch_user")
        indexed_games = defaultdict(list)

        for game in all_games:
            indexed_games[game.match_id].append(game)
        for match in matches:
            games = indexed_games[match.id]
            game_data[match.id] = [
                [
                    game.winner.twitch_user.username,
                    game.losing_score,
                    game.ended_at.astimezone(pytz.utc).isoformat()
                ]
                for game in games
            ]
        return game_data
