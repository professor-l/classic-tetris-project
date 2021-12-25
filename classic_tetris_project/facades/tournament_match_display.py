class TournamentMatchDisplay:
    def __init__(self, tournament_match, user):
        self.tournament_match = tournament_match
        self.user = user

    def can_restream(self):
        return (self.tournament_match.restreamed and self.tournament_match.is_playable() and
                self.user and self.user.permissions.restream())
