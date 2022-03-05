from django.utils.html import format_html

import math

from ..models import TournamentMatch


class TournamentMatchDisplay:
    def __init__(self, tournament_match, user=None, player_count=16):
        self.tournament_match = tournament_match
        self.user = user
        self.player_count = player_count

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

    def player1_color(self):
        player_count = self.tournament_match.tournament.seed_count
        return self.get_color_for_player_index(player_count, self.tournament_match, 1)


    def player2_color(self):
        player_count = self.tournament_match.tournament.seed_count
        return self.get_color_for_player_index(player_count, self.tournament_match, 0)

    @staticmethod
    def generate_round(match_count, all_matches):
        new_matches = []
        matches_to_generate = match_count if len(all_matches) >= match_count else len(all_matches)
        for _ in range(matches_to_generate):
            next_match = {}
            if len(all_matches) != 0:
                next_match = all_matches.pop(0)
            new_matches.append(next_match)
        
        new_matches.reverse()
        return new_matches

    @staticmethod
    def get_color_for_player_index(player_count, match, player_position):
        round_num = match.round_number
        adjusted_round_num = round_num if (player_count & (player_count-1) == 0) and player_count != 0 else round_num - 1
        adjusted_round_num = adjusted_round_num or 1

        player_count = match.tournament.seed_count
        adjusted_player_count = TournamentMatchDisplay.highest_power_of_2(player_count)
        color_section_count = adjusted_player_count / 4
        match_num = match.match_number


        mod_value = (adjusted_player_count / 2**(adjusted_round_num-1)) if adjusted_round_num > 1 else adjusted_player_count
        player_index = (match_num * 2 - player_position) % mod_value or mod_value

        color_index = 1
        if player_index > (color_section_count / 2**(adjusted_round_num - 1)):
            color_index = 2
        if player_index > (color_section_count / 2**(adjusted_round_num - 1))*2:
            color_index = 3
        if player_index > (color_section_count / 2**(adjusted_round_num - 1))*3:
            color_index = 4

        return color_index or color_section_count if adjusted_round_num < math.log2(adjusted_player_count) else 5

    @staticmethod
    def highest_power_of_2(n):
        res = 0
        for i in range(n, 0, -1):
            # If i is a power of 2
            if ((i & (i - 1)) == 0):
                res = i
                break
            
        return res