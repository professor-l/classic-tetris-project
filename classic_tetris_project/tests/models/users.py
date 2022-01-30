from classic_tetris_project.test_helper import *

class User_(Spec):
    @lazy
    def user(self):
        return UserFactory()
    @lazy
    def discord_user(self):
        return DiscordUserFactory(user=self.user)
    @lazy
    def twitch_user(self):
        return TwitchUserFactory(user=self.user)
    @lazy
    def other_user(self):
        return UserFactory()

    class add_pb:
        def test_creates_score_pb(self):
            assert_that(ScorePB.objects.count(), equal_to(0))

            self.user.add_pb(200000)

            assert_that(ScorePB.objects.count(), equal_to(1))
            assert_that(ScorePB.objects.last(), has_properties(
                user=equal_to(self.user),
                current=equal_to(True),
                score=equal_to(200000),
                console_type=equal_to("ntsc"),
                starting_level=equal_to(None),
                lines=equal_to(None),
            ))

        def test_with_params_creates_score_pb(self):
            assert_that(ScorePB.objects.count(), equal_to(0))

            self.user.add_pb(200000, console_type="pal", starting_level=18, lines=30)

            assert_that(ScorePB.objects.count(), equal_to(1))
            assert_that(ScorePB.objects.last(), has_properties(
                user=equal_to(self.user),
                current=equal_to(True),
                score=equal_to(200000),
                console_type=equal_to("pal"),
                starting_level=equal_to(18),
                lines=equal_to(30),
            ))

        def test_with_existing_replaces_current(self):
            score_pb_other = ScorePBFactory()
            score_pb_pal = ScorePBFactory(user=self.user, console_type="pal")
            score_pb_19 = ScorePBFactory(user=self.user, starting_level=19)
            score_pb = ScorePBFactory(user=self.user)

            self.user.add_pb(200000)
            score_pb_other.refresh_from_db()
            score_pb_pal.refresh_from_db()
            score_pb_19.refresh_from_db()
            score_pb.refresh_from_db()

            assert_that(score_pb_other.current, equal_to(True))
            assert_that(score_pb_pal.current, equal_to(True))
            assert_that(score_pb_19.current, equal_to(True))
            assert_that(score_pb.current, equal_to(False))

    class get_pb:
        def test_without_score_pbs_returns_none(self):
            score_pb_other = self.other_user.add_pb(999999)

            assert_that(self.user.get_pb(), equal_to(None))

        def test_returns_greatest_score(self):
            score_pb_other = self.other_user.add_pb(999999)

            score_pb_accident = self.user.add_pb(2000000)
            score_pb_old = self.user.add_pb(200000)
            score_pb_18_old = self.user.add_pb(200000, starting_level=18)
            score_pb_18 = self.user.add_pb(400000, starting_level=18)
            score_pb_19 = self.user.add_pb(300000, starting_level=19)
            score_pb_pal_old = self.user.add_pb(300000, console_type="pal")
            score_pb_pal = self.user.add_pb(500000, console_type="pal")

            assert_that(self.user.get_pb(), equal_to(400000))
            assert_that(self.user.get_pb(starting_level=18), equal_to(400000))
            assert_that(self.user.get_pb(starting_level=19), equal_to(300000))
            assert_that(self.user.get_pb(console_type="pal"), equal_to(500000))

    class display_name:
        def test_with_twitch_user(self):
            self.discord_user
            self.twitch_user
            self.user.preferred_name = "Preferred Name"
            assert_that(self.user.display_name, equal_to(self.twitch_user.username))

        def test_with_preferred_name(self):
            self.discord_user
            self.user.preferred_name = "Preferred Name"
            assert_that(self.user.display_name, equal_to("Preferred Name"))

        def test_with_discord_user(self):
            self.discord_user
            assert_that(self.user.display_name, equal_to(self.discord_user.username))

        def test_with_nothing(self):
            assert_that(self.user.display_name, equal_to(f"User {self.user.id}"))

    class preferred_display_name:
        def test_with_preferred_name(self):
            self.discord_user
            self.twitch_user
            self.user.preferred_name = "Preferred Name"
            assert_that(self.user.preferred_display_name, equal_to("Preferred Name"))

        def test_with_twitch_user(self):
            self.discord_user
            self.twitch_user
            assert_that(self.user.preferred_display_name, equal_to(self.twitch_user.username))

        def test_with_discord_user(self):
            self.discord_user
            assert_that(self.user.preferred_display_name, equal_to(self.discord_user.username))

        def test_with_nothing(self):
            assert_that(self.user.preferred_display_name, equal_to(f"User {self.user.id}"))

    class profile_id:
        def test_with_twitch_user(self):
            self.twitch_user
            assert_that(self.user.profile_id(), equal_to(self.twitch_user.username))

        def test_without_twitch_user(self):
            assert_that(self.user.profile_id(), equal_to(self.user.id))

    class get_absolute_url:
        def test_with_twitch_user(self):
            self.twitch_user
            assert_that(self.user.get_absolute_url(),
                        equal_to(f"/user/{self.twitch_user.username}/"))

        def test_without_twitch_user(self):
            assert_that(self.user.get_absolute_url(),
                        equal_to(f"/user/{self.user.id}/"))

        @patch("django.conf.settings.BASE_URL", "https://monthlytetris.info")
        def test_with_include_base(self):
            assert_that(self.user.get_absolute_url(True),
                        equal_to(f"https://monthlytetris.info/user/{self.user.id}/"))


class DiscordUser_(Spec):
    @lazy
    def discord_user(self):
        return DiscordUserFactory(discord_id="1001", username="User 1", discriminator="9001")
    @lazy
    def discord_user_old(self):
        return DiscordUserFactory(discord_id="1001", username="User 1 old", discriminator="8001")
    @lazy
    def discord_user_other(self):
        return DiscordUserFactory(discord_id="1002", username="User 2", discriminator="9002")
    @lazy
    def user_obj(self):
        return discord.wrap_user_dict({ "id": "1001", "username": "User 1", "discriminator": "9001",
                                       "avatar": "1001" })

    class get_or_create_from_user_obj:
        def test_returns_existing_user(self):
            existing_discord_user = self.discord_user
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            assert_that(discord_user, equal_to(existing_discord_user))

        def test_updates_existing_user(self):
            existing_discord_user = self.discord_user_old
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            assert_that(discord_user, equal_to(existing_discord_user))
            existing_discord_user.refresh_from_db()
            assert_that(existing_discord_user.username, equal_to("User 1"))
            assert_that(existing_discord_user.discriminator, equal_to("9001"))

        def test_creates_user(self):
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            assert_that(DiscordUser.objects.count(), equal_to(1))
            assert_that(discord_user.discord_id, equal_to("1001"))
            assert_that(discord_user.username, equal_to("User 1"))
            assert_that(discord_user.discriminator, equal_to("9001"))

    class username_with_descriminator:
        def test_returns_correct_value(self):
            self.discord_user.username = "Username"
            self.discord_user.discriminator = "1234"
            assert_that(self.discord_user.username_with_discriminator, equal_to("Username#1234"))

    class update_fields:
        def test_updates_fields(self):
            self.discord_user_old.update_fields(self.user_obj)

            self.discord_user_old.refresh_from_db()
            assert_that(self.discord_user_old.username, equal_to("User 1"))
            assert_that(self.discord_user_old.discriminator, equal_to("9001"))

        def test_doesnt_save_if_no_change(self):
            self.discord_user
            with patch.object(DiscordUser, "save") as save:
                self.discord_user.update_fields(self.user_obj)

            assert_that(self.discord_user.username, equal_to("User 1"))
            assert_that(self.discord_user.discriminator, equal_to("9001"))
            save.assert_not_called()

        def test_complains_given_wrong_id(self):
            assert_that(calling(self.discord_user_other.update_fields).with_args(self.user_obj),
                        raises(Exception))


class TwitchUser_(Spec):
    @lazy
    def twitch_user(self):
        return TwitchUserFactory()

    class from_username:
        def test_with_existing_user(self):
            assert_that(TwitchUser.from_username(self.twitch_user.username),
                        equal_to(self.twitch_user))

        def test_without_existing_user(self):
            assert_that(TwitchUser.from_username("nonexistent"), equal_to(None))

        @patch.object(twitch.APIClient, "user_from_username")
        def test_refetch_without_result(self, api_patch):
            api_patch.return_value = None

            assert_that(TwitchUser.from_username("nonexistent", True), equal_to(None))

        @patch.object(twitch.APIClient, "user_from_username")
        def test_refetch_without_matching_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="no_match")

            assert_that(TwitchUser.from_username("no_match", True), equal_to(None))

        @patch.object(twitch.APIClient, "user_from_username")
        def test_refetch_with_matching_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="match",
                                                              id=self.twitch_user.twitch_id)

            assert_that(TwitchUser.from_username("match", True), equal_to(self.twitch_user))
            self.twitch_user.refresh_from_db()
            assert_that(self.twitch_user.username, equal_to("match"))

    class get_or_create_from_username:
        def test_with_existing_user(self):
            assert_that(TwitchUser.get_or_create_from_username(self.twitch_user.username),
                        equal_to(self.twitch_user))

        @patch.object(twitch.APIClient, "user_from_username")
        def test_with_new_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="new_user", id="12345")

            new_twitch_user = TwitchUser.get_or_create_from_username("new_user")
            assert_that(new_twitch_user.username, equal_to("new_user"))
            assert_that(new_twitch_user.twitch_id, equal_to("12345"))

        @patch.object(twitch.APIClient, "user_from_username")
        def test_with_updated_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="updated_user",
                                                              id=self.twitch_user.twitch_id)

            assert_that(TwitchUser.get_or_create_from_username("updated_user"),
                        equal_to(self.twitch_user))
            self.twitch_user.refresh_from_db()
            assert_that(self.twitch_user.username, equal_to("updated_user"))
            assert_that(TwitchUser.objects.count(), equal_to(1))

        @patch.object(twitch.APIClient, "user_from_username")
        def test_with_nonexistent_user(self, api_patch):
            api_patch.return_value = None

            assert_that(calling(TwitchUser.get_or_create_from_username).with_args("nonexistent_user"),
                        raises(Exception))

    class get_or_create_from_user_obj:
        def test_with_existing_user(self):
            user_obj = MockTwitchAPIUser.create(username=self.twitch_user.username,
                                                id=self.twitch_user.twitch_id)

            assert_that(TwitchUser.get_or_create_from_user_obj(user_obj),
                        equal_to(self.twitch_user))

        def test_with_updated_user(self):
            user_obj = MockTwitchAPIUser.create(username="updated_user",
                                                id=self.twitch_user.twitch_id)

            assert_that(TwitchUser.get_or_create_from_user_obj(user_obj),
                        equal_to(self.twitch_user))
            self.twitch_user.refresh_from_db()
            assert_that(self.twitch_user.username, equal_to("updated_user"))

        def test_without_existing_user(self):
            user_obj = MockTwitchAPIUser.create(username="new_user", id="12345")

            new_twitch_user = TwitchUser.get_or_create_from_user_obj(user_obj)
            assert_that(new_twitch_user.username, equal_to("new_user"))
            assert_that(new_twitch_user.twitch_id, equal_to("12345"))
            assert_that(TwitchUser.objects.count(), equal_to(1))

    class twitch_url:
        def test_returns_twitch_url(self):
            self.twitch_user.username = "dexfore"
            assert_that(self.twitch_user.twitch_url, equal_to("https://www.twitch.tv/dexfore"))
