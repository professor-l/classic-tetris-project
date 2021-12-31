from classic_tetris_project.test_helper import *
from classic_tetris_project.util.merge import UserMerger

class UserMerger_(Spec):
    @lazy
    def user1(self):
        return UserFactory()
    @lazy
    def user2(self):
        return UserFactory()
    @lazy
    def merger(self):
        return UserMerger(self.user1, self.user2)

    class merge:
        def test_merges_users_successfully(self):
            discord_user = DiscordUserFactory(user=self.user1)
            twitch_user = TwitchUserFactory(user=self.user2)
            self.merger.merge()

            discord_user.refresh_from_db()
            twitch_user.refresh_from_db()
            assert_that(discord_user.user, equal_to(self.user1))
            assert_that(twitch_user.user, equal_to(self.user1))
            assert_that(calling(self.user2.refresh_from_db), raises(User.DoesNotExist))

        def test_merges_into_discord_user(self):
            discord_user = DiscordUserFactory(user=self.user2)
            twitch_user = TwitchUserFactory(user=self.user1)
            self.merger.merge()

            discord_user.refresh_from_db()
            twitch_user.refresh_from_db()
            assert_that(discord_user.user, equal_to(self.user2))
            assert_that(twitch_user.user, equal_to(self.user2))
            assert_that(calling(self.user1.refresh_from_db), raises(User.DoesNotExist))

        def test_fails_with_two_discord_users(self):
            discord_user = DiscordUserFactory(user=self.user1)
            discord_user2 = DiscordUserFactory(user=self.user2)
            twitch_user = TwitchUserFactory(user=self.user2)

            assert_that(calling(self.merger.merge), raises(UserMerger.MergeError))
            discord_user.refresh_from_db()
            twitch_user.refresh_from_db()
            assert_that(discord_user.user, equal_to(self.user1))
            assert_that(twitch_user.user, equal_to(self.user2))

        def test_fails_with_two_twitch_users(self):
            discord_user = DiscordUserFactory(user=self.user1)
            twitch_user = TwitchUserFactory(user=self.user2)
            twitch_user2 = TwitchUserFactory(user=self.user1)

            assert_that(calling(self.merger.merge), raises(UserMerger.MergeError))
            discord_user.refresh_from_db()
            twitch_user.refresh_from_db()
            assert_that(discord_user.user, equal_to(self.user1))
            assert_that(twitch_user.user, equal_to(self.user2))
