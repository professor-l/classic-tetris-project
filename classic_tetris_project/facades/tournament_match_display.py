from django.utils.html import format_html

from ..models import TournamentMatch


class TournamentMatchDisplay:
    def __init__(self, tournament_match, user=None):
        self.tournament_match = tournament_match
        self.user = user

    def can_restream(self):
        return (self.user and
                ((self.tournament_match.restreamed and self.user.permissions.restream()) or
                 self.user.permissions.report_all()) and
                self.tournament_match.is_playable())

    def status_tag(self):
        def render_tag(text, style):
            return format_html(
                "<span class='status-tag status-tag--{}'>{}</span>",
                style,
                text
            )

        if self.tournament_match.is_complete():
            return render_tag("Complete", "green")
        elif self.tournament_match.is_scheduled():
            return render_tag("Scheduled", "yellow")
        elif self.tournament_match.is_playable():
            return render_tag("Playable", "gray")

    def display_name_from_source(self, source_type, source_data):
        if source_type == TournamentMatch.PlayerSource.NONE:
            return None
        elif source_type == TournamentMatch.PlayerSource.SEED:
            return f"Seed {source_data}"
        elif source_type == TournamentMatch.PlayerSource.MATCH_WINNER:
            return f"Winner of Match {source_data}"
        elif source_type == TournamentMatch.PlayerSource.MATCH_LOSER:
            return f"Loser of Match {source_data}"

    def player1_display_name(self):
        if self.tournament_match.player1:
            return self.tournament_match.player1.display_name()
        else:
            return self.display_name_from_source(self.tournament_match.source1_type,
                                                 self.tournament_match.source1_data)

    def player2_display_name(self):
        if self.tournament_match.player2:
            return self.tournament_match.player2.display_name()
        else:
            return self.display_name_from_source(self.tournament_match.source2_type,
                                                 self.tournament_match.source2_data)
