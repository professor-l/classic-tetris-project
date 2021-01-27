from classic_tetris_project.test_helper import *

class Event_(Spec):
    @lazy
    def event(self):
        return EventFactory()
    @lazy
    def user(self):
        return UserFactory()
    @lazy
    def discord_user(self):
        return DiscordUserFactory(user=self.user)
    @lazy
    def twitch_user(self):
        return TwitchUserFactory(user=self.user)

    class is_user_eligible:
        def test_returns_true_if_eligible(self):
            self.discord_user
            self.twitch_user
            self.event.qualifying_open = True
            self.event.save()

            assert_that(self.event.is_user_eligible(self.user), equal_to(True))

        def test_returns_false_if_ineligible(self):
            assert_that(self.event.is_user_eligible(self.user), equal_to(False))

    class user_ineligible_reason:
        def setup(self):
            super().setup()
            self.discord_user
            self.twitch_user
            self.event.qualifying_open = True
            self.event.save()

        def test_returns_none_if_eligible(self):
            assert_that(self.event.user_ineligible_reason(self.user), equal_to(None))

        def test_returns_closed(self):
            self.event.qualifying_open = False
            self.event.save()

            assert_that(self.event.user_ineligible_reason(self.user), equal_to("closed"))

        def test_returns_logged_out(self):
            assert_that(self.event.user_ineligible_reason(None), equal_to("logged_out"))

        def test_returns_already_qualified(self):
            QualifierFactory(user=self.user, event=self.event)

            assert_that(self.event.user_ineligible_reason(self.user), equal_to("already_qualified"))

        def test_returns_link_twitch(self):
            self.twitch_user.delete()
            self.user.refresh_from_db()

            assert_that(self.event.user_ineligible_reason(self.user), equal_to("link_twitch"))

        def test_returns_link_discord(self):
            self.discord_user.delete()
            self.user.refresh_from_db()

            assert_that(self.event.user_ineligible_reason(self.user), equal_to("link_discord"))


class Qualifier_(Spec):
    @lazy
    def qualifier(self):
        return QualifierFactory()

    class review:
        def test_sets_reviewer_columns(self):
            reviewer = UserFactory()
            self.qualifier.review(True, reviewer, notes="Great job", checks={
                "announced": True,
                "stencil": True,
                "rom": True,
                "timer": True,
                "reset": True,
            })
            assert_that(self.qualifier, has_properties(
                approved=True,
                reviewed_by=reviewer,
                review_data={
                    "notes": "Great job",
                    "checks": {
                        "announced": True,
                        "stencil": True,
                        "rom": True,
                        "timer": True,
                        "reset": True,
                    },
                }
            ))
