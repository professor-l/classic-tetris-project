from ..util import lazy

class UserPermissions:
    REVIEW_QUALIFIERS = "classic_tetris_project.change_qualifier"
    RESTREAM = "classic_tetris_project.restream"
    REPORT_ALL = "classic_tetris_project.change_tournamentmatch"
    CHANGE_TOURNAMENT = "classic_tetris_project.change_tournament"
    SEND_LIVE_NOTIFICATIONS = "classic_tetris_project.send_live_notifications"

    def __init__(self, user):
        self.user = user

    @lazy
    def auth_user(self):
        if (self.user and hasattr(self.user, "website_user")
                and hasattr(self.user.website_user, "auth_user")):
            return self.user.website_user.auth_user

    def review_qualifiers(self):
        return self.auth_user is not None and self.auth_user.has_perm(self.REVIEW_QUALIFIERS)

    def restream(self):
        return self.auth_user is not None and self.auth_user.has_perm(self.RESTREAM)

    def report_all(self):
        return self.auth_user is not None and self.auth_user.has_perm(self.REPORT_ALL)

    def change_tournament(self):
        return self.auth_user is not None and self.auth_user.has_perm(self.CHANGE_TOURNAMENT)

    def send_live_notifications(self):
        return self.auth_user is not None and self.auth_user.has_perm(self.SEND_LIVE_NOTIFICATIONS)
