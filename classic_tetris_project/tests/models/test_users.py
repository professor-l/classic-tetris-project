from classic_tetris_project.tests.helper import *

class UserTestCase(TestCase):
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


    with describe("#add_pb"):
        def test_add_pb_creates_score_pb(self):
            self.assertEqual(ScorePB.objects.count(), 0)

            self.user.add_pb(200000)

            self.assertEqual(ScorePB.objects.count(), 1)
            score_pb = ScorePB.objects.last()
            self.assertEqual(score_pb.user, self.user)
            self.assertEqual(score_pb.current, True)
            self.assertEqual(score_pb.score, 200000)
            self.assertEqual(score_pb.console_type, "ntsc")
            self.assertEqual(score_pb.starting_level, None)
            self.assertEqual(score_pb.lines, None)

        def test_add_pb_with_params_creates_score_pb(self):
            self.assertEqual(ScorePB.objects.count(), 0)

            self.user.add_pb(200000, console_type="pal", starting_level=18, lines=30)

            self.assertEqual(ScorePB.objects.count(), 1)
            score_pb = ScorePB.objects.last()
            self.assertEqual(score_pb.user, self.user)
            self.assertEqual(score_pb.current, True)
            self.assertEqual(score_pb.score, 200000)
            self.assertEqual(score_pb.console_type, "pal")
            self.assertEqual(score_pb.starting_level, 18)
            self.assertEqual(score_pb.lines, 30)

        def test_add_pb_with_existing_replaces_current(self):
            score_pb_other = ScorePBFactory()
            score_pb_pal = ScorePBFactory(user=self.user, console_type="pal")
            score_pb_19 = ScorePBFactory(user=self.user, starting_level=19)
            score_pb = ScorePBFactory(user=self.user)

            self.user.add_pb(200000)
            score_pb_other.refresh_from_db()
            score_pb_pal.refresh_from_db()
            score_pb_19.refresh_from_db()
            score_pb.refresh_from_db()

            self.assertEqual(score_pb_other.current, True)
            self.assertEqual(score_pb_pal.current, True)
            self.assertEqual(score_pb_19.current, True)
            self.assertEqual(score_pb.current, False)


    with describe("#get_pb"):
        def test_get_pb_without_score_pbs_returns_none(self):
            score_pb_other = self.other_user.add_pb(999999)

            self.assertEqual(self.user.get_pb(), None)

        def test_get_pb_returns_greatest_score(self):
            score_pb_other = self.other_user.add_pb(999999)

            score_pb_accident = self.user.add_pb(2000000)
            score_pb_old = self.user.add_pb(200000)
            score_pb_18_old = self.user.add_pb(200000, starting_level=18)
            score_pb_18 = self.user.add_pb(400000, starting_level=18)
            score_pb_19 = self.user.add_pb(300000, starting_level=19)
            score_pb_pal_old = self.user.add_pb(300000, console_type="pal")
            score_pb_pal = self.user.add_pb(500000, console_type="pal")

            self.assertEqual(self.user.get_pb(), 400000)
            self.assertEqual(self.user.get_pb(starting_level=18), 400000)
            self.assertEqual(self.user.get_pb(starting_level=19), 300000)
            self.assertEqual(self.user.get_pb(console_type="pal"), 500000)

    with describe("#display_name"):
        def test_display_name_with_preferred_name(self):
            self.discord_user
            self.twitch_user
            self.user.preferred_name = "Preferred Name"
            self.assertEqual(self.user.display_name, "Preferred Name")

        def test_display_name_with_twitch_user(self):
            self.discord_user
            self.twitch_user
            self.assertEqual(self.user.display_name, self.twitch_user.username)

        def test_display_name_with_discord_user(self):
            self.discord_user
            self.assertEqual(self.user.display_name, self.discord_user.username)

        def test_display_name_with_nothing(self):
            self.assertEqual(self.user.display_name, f"User {self.user.id}")

    with describe("#profile_id"):
        def test_profile_id_with_twitch_user(self):
            self.twitch_user
            self.assertEqual(self.user.profile_id(), self.twitch_user.username)

        def test_profile_id_without_twitch_user(self):
            self.assertEqual(self.user.profile_id(), self.user.id)

    with describe("#get_absolute_url"):
        def test_get_absolute_url_with_twitch_user(self):
            self.twitch_user
            self.assertEqual(self.user.get_absolute_url(), f"/user/{self.twitch_user.username}/")

        def test_get_absolute_url_without_twitch_user(self):
            self.assertEqual(self.user.get_absolute_url(), f"/user/{self.user.id}/")

        @patch("django.conf.settings.BASE_URL", "https://monthlytetris.info")
        def test_get_absolute_url_with_include_base(self):
            self.assertEqual(self.user.get_absolute_url(True),
                             f"https://monthlytetris.info/user/{self.user.id}/")


class DiscordUserTestCase(TestCase):
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

    with describe(".get_or_create_from_user_obj"):
        def test_get_or_create_from_user_obj_returns_existing_user(self):
            existing_discord_user = self.discord_user
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            self.assertEqual(discord_user, existing_discord_user)

        def test_get_or_create_from_user_obj_updates_existing_user(self):
            existing_discord_user = self.discord_user_old
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            self.assertEqual(discord_user, existing_discord_user)
            existing_discord_user.refresh_from_db()
            self.assertEqual(existing_discord_user.username, "User 1")
            self.assertEqual(existing_discord_user.discriminator, "9001")

        def test_get_or_create_from_user_obj_creates_user(self):
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            self.assertEqual(DiscordUser.objects.count(), 1)
            self.assertEqual(discord_user.discord_id, "1001")
            self.assertEqual(discord_user.username, "User 1")
            self.assertEqual(discord_user.discriminator, "9001")

    with describe("#username_with_discriminator"):
        def test_username_with_discriminator(self):
            self.discord_user.username = "Username"
            self.discord_user.discriminator = "1234"
            self.assertEqual(self.discord_user.username_with_discriminator, "Username#1234")

    with describe("#update_fields"):
        def test_update_fields_updates_fields(self):
            self.discord_user_old.update_fields(self.user_obj)

            self.discord_user_old.refresh_from_db()
            self.assertEqual(self.discord_user_old.username, "User 1")
            self.assertEqual(self.discord_user_old.discriminator, "9001")

        def test_update_fields_doesnt_save_if_no_change(self):
            self.discord_user
            with patch.object(DiscordUser, "save") as save:
                self.discord_user.update_fields(self.user_obj)

            self.assertEqual(self.discord_user.username, "User 1")
            self.assertEqual(self.discord_user.discriminator, "9001")
            save.assert_not_called()

        def test_update_fields_complains_given_wrong_id(self):
            with self.assertRaises(Exception):
                self.discord_user_other.update_fields(self.user_obj)


class TwitchUserTestCase(TestCase):
    @lazy
    def twitch_user(self):
        return TwitchUserFactory()

    with describe(".from_username"):
        def test_from_username_with_existing_user(self):
            self.assertEqual(TwitchUser.from_username(self.twitch_user.username), self.twitch_user)

        def test_from_username_without_existing_user(self):
            self.assertEqual(TwitchUser.from_username("nonexistent"), None)

        @patch.object(twitch.APIClient, "user_from_username")
        def test_from_username_refetch_without_result(self, api_patch):
            api_patch.return_value = None

            self.assertEqual(TwitchUser.from_username("nonexistent", True), None)

        @patch.object(twitch.APIClient, "user_from_username")
        def test_from_username_refetch_without_matching_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="no_match")

            self.assertEqual(TwitchUser.from_username("no_match", True), None)

        @patch.object(twitch.APIClient, "user_from_username")
        def test_from_username_refetch_with_matching_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="match",
                                                              id=self.twitch_user.twitch_id)

            self.assertEqual(TwitchUser.from_username("match", True), self.twitch_user)
            self.twitch_user.refresh_from_db()
            self.assertEqual(self.twitch_user.username, "match")

    with describe(".get_or_create_from_username"):
        def test_get_or_create_from_username_with_existing_user(self):
            self.assertEqual(TwitchUser.get_or_create_from_username(self.twitch_user.username), self.twitch_user)

        @patch.object(twitch.APIClient, "user_from_username")
        def test_get_or_create_from_username_with_new_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="new_user", id="12345")

            new_twitch_user = TwitchUser.get_or_create_from_username("new_user")
            self.assertEqual(new_twitch_user.username, "new_user")
            self.assertEqual(new_twitch_user.twitch_id, "12345")

        @patch.object(twitch.APIClient, "user_from_username")
        def test_get_or_create_from_username_with_updated_user(self, api_patch):
            api_patch.return_value = MockTwitchAPIUser.create(username="updated_user",
                                                              id=self.twitch_user.twitch_id)

            self.assertEqual(TwitchUser.get_or_create_from_username("updated_user"), self.twitch_user)
            self.twitch_user.refresh_from_db()
            self.assertEqual(self.twitch_user.username, "updated_user")
            self.assertEqual(TwitchUser.objects.count(), 1)

        @patch.object(twitch.APIClient, "user_from_username")
        def test_get_or_create_from_username_with_nonexistent_user(self, api_patch):
            api_patch.return_value = None

            with self.assertRaises(Exception):
                TwitchUser.get_or_create_from_username("nonexistent_user")

    with describe(".get_or_create_from_user_obj"):
        def test_get_or_create_from_user_obj_with_existing_user(self):
            user_obj = MockTwitchAPIUser.create(username=self.twitch_user.username,
                                                id=self.twitch_user.twitch_id)

            self.assertEqual(TwitchUser.get_or_create_from_user_obj(user_obj), self.twitch_user)

        def test_get_or_create_from_user_obj_with_updated_user(self):
            user_obj = MockTwitchAPIUser.create(username="updated_user",
                                                id=self.twitch_user.twitch_id)

            self.assertEqual(TwitchUser.get_or_create_from_user_obj(user_obj), self.twitch_user)
            self.twitch_user.refresh_from_db()
            self.assertEqual(self.twitch_user.username, "updated_user")

        def test_get_or_create_from_user_obj_without_existing_user(self):
            user_obj = MockTwitchAPIUser.create(username="new_user", id="12345")

            new_twitch_user = TwitchUser.get_or_create_from_user_obj(user_obj)
            self.assertEqual(new_twitch_user.username, "new_user")
            self.assertEqual(new_twitch_user.twitch_id, "12345")
            self.assertEqual(TwitchUser.objects.count(), 1)

    with describe("#twitch_url"):
        def test_twitch_url(self):
            self.twitch_user.username = "dexfore"
            self.assertEqual(self.twitch_user.twitch_url, "https://www.twitch.tv/dexfore")
