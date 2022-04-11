from django.core.management.base import BaseCommand

from classic_tetris_project.util.match_sheet_reporter import MatchSheetReporter

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        reporter = MatchSheetReporter()
        match_count = reporter.sync_all()
        self.stdout.write(f"Reported {match_count} matches")
