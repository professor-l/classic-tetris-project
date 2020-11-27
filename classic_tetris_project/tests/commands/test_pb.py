from classic_tetris_project.tests.helper import *

class GetPBCommandTestCase(CommandTestCase):
    with describe("discord"):
        def test_discord_with_no_user(self):
            self.assertDiscord("!pb", [
                "User has not set a PB."
            ])

        def test_discord_with_no_pb(self):
            self.discord_user

            self.assertDiscord("!pb", [
                "User has not set a PB."
            ])

        def test_discord_with_ntsc_pb(self):
            self.discord_user.user.add_pb(100000)

            self.assertDiscord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 100,000."
            ])

        def test_discord_with_ntsc_18_and_19_pb(self):
            self.discord_user.user.add_pb(600000, starting_level=18)
            self.discord_user.user.add_pb(100000, starting_level=19)

            self.assertDiscord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 600,000 (100,000 19 start)."
            ])

        def test_discord_with_pal_pb(self):
            self.discord_user.user.add_pb(100000, console_type="pal")

            self.assertDiscord("!pb", [
                f"{self.discord_api_user.name} has a PAL PB of 100,000."
            ])

        def test_discord_with_ntsc_and_pal_pb(self):
            self.discord_user.user.add_pb(200000, console_type="ntsc")
            self.discord_user.user.add_pb(100000, console_type="pal")

            self.assertDiscord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 200,000 and a PAL PB of 100,000."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username",
               return_value=None)
        def test_discord_with_nonexistent_user(self, _):
            self.assertDiscord("!pb Other User", [
                "User has not set a PB."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_discord_with_user_with_no_pb(self, any_platform_user_from_username):
            discord_user = DiscordUserFactory(username="Other User")
            any_platform_user_from_username.return_value = discord_user

            self.assertDiscord("!pb Other User", [
                "User has not set a PB."
            ])

            any_platform_user_from_username.assert_called_once_with("Other User")

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_discord_with_user_with_pb(self, any_platform_user_from_username):
            discord_user = DiscordUserFactory(username="Other User")
            discord_user.user.add_pb(100000)
            any_platform_user_from_username.return_value = discord_user

            self.assertDiscord("!pb Other User", [
                "Other User has an NTSC PB of 100,000."
            ])

            any_platform_user_from_username.assert_called_once_with("Other User")

    with describe("twitch"):
        @patch.object(twitch.APIClient, "user_from_id",
                      lambda self, user_id, client=None: MockTwitchAPIUser.create(id=user_id))
        def test_twitch_with_no_user(self):
            self.assertTwitch("!pb", [
                "User has not set a PB."
            ])

        def test_twitch_with_no_pb(self):
            self.twitch_user

            self.assertTwitch("!pb", [
                "User has not set a PB."
            ])

        def test_twitch_with_ntsc_pb(self):
            self.twitch_user.user.add_pb(100000)

            self.assertTwitch("!pb", [
                f"{self.twitch_api_user.username} has an NTSC PB of 100,000."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username",
               return_value=None)
        def test_twitch_with_nonexistent_user(self, _):
            self.assertTwitch("!pb other_user", [
                "User has not set a PB."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_twitch_with_user_with_no_pb(self, any_platform_user_from_username):
            twitch_user = TwitchUserFactory(username="other_user")
            any_platform_user_from_username.return_value = twitch_user

            self.assertTwitch("!pb other_user", [
                "User has not set a PB."
            ])

            any_platform_user_from_username.assert_called_once_with("other_user")

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_twitch_with_user_with_pb(self, any_platform_user_from_username):
            twitch_user = TwitchUserFactory(username="other_user")
            twitch_user.user.add_pb(100000)
            any_platform_user_from_username.return_value = twitch_user

            self.assertTwitch("!pb other_user", [
                "other_user has an NTSC PB of 100,000."
            ])

            any_platform_user_from_username.assert_called_once_with("other_user")


class SetPBCommandTestCase(CommandTestCase):
    with describe("discord"):
        def test_discord_with_no_args(self):
            self.assertDiscord("!setpb", [re.compile("^Usage:")])

        def test_discord_with_no_user(self):
            self.assertDiscord("!setpb 100,000", [
                f"<@{self.discord_api_user.id}> has a new NTSC PB of 100,000!"
            ])

            self.assertEqual(User.objects.count(), 1)
            self.assertEqual(ScorePB.objects.count(), 1)
            user = User.objects.last()
            self.assertEqual(user.get_pb(), 100000)

        def test_discord_with_user(self):
            self.discord_user

            self.assertDiscord("!setpb 100000", [
                f"<@{self.discord_api_user.id}> has a new NTSC PB of 100,000!"
            ])

            self.assertEqual(User.objects.count(), 1)
            self.assertEqual(ScorePB.objects.count(), 1)
            self.assertEqual(self.discord_user.user.get_pb(), 100000)

        def test_discord_level(self):
            self.assertDiscord("!setpb 100000 NTSC 19", [
                f"<@{self.discord_api_user.id}> has a new NTSC level 19 PB of 100,000!"
            ])

            self.assertEqual(ScorePB.objects.count(), 1)
            self.assertEqual(User.objects.last().get_pb(console_type="ntsc", starting_level=19), 100000)

        def test_discord_pal(self):
            self.assertDiscord("!setpb 100000 PAL", [
                f"<@{self.discord_api_user.id}> has a new PAL PB of 100,000!"
            ])

            self.assertEqual(ScorePB.objects.count(), 1)
            self.assertEqual(User.objects.last().get_pb(console_type="pal"), 100000)

        def test_discord_errors(self):
            self.assertDiscord("!setpb asdf", [re.compile("^Usage:")])
            self.assertDiscord("!setpb -5", ["Invalid PB."])
            self.assertDiscord("!setpb 1600000", ["You wish, kid >.>"])
            self.assertDiscord("!setpb 100000 NTSC -5", ["Invalid level."])
            self.assertDiscord("!setpb 100000 NTSC 30", ["Invalid level."])
            self.assertDiscord("!setpb 100000 foo", [re.compile("^Invalid PB type")])

    with describe("twitch"):
        def test_twitch_with_no_args(self):
            self.assertTwitch("!setpb", [re.compile("Usage:")])

        @patch.object(twitch.APIClient, "user_from_id",
                      lambda self, user_id, client=None: MockTwitchAPIUser.create(id=user_id))
        def test_twitch_with_no_user(self):
            self.twitch_channel
            self.assertEqual(User.objects.count(), 1)

            self.assertTwitch("!setpb 100,000", [
                f"@{self.twitch_api_user.username} has a new NTSC PB of 100,000!"
            ])

            self.assertEqual(User.objects.count(), 2)
            self.assertEqual(ScorePB.objects.count(), 1)
            user = User.objects.last()
            self.assertEqual(user.get_pb(), 100000)

        def test_twitch_with_user(self):
            self.twitch_channel
            self.twitch_user
            self.assertEqual(User.objects.count(), 2)

            self.assertTwitch("!setpb 100000", [
                f"@{self.twitch_api_user.username} has a new NTSC PB of 100,000!"
            ])

            self.assertEqual(User.objects.count(), 2)
            self.assertEqual(ScorePB.objects.count(), 1)
            self.assertEqual(self.twitch_user.user.get_pb(), 100000)
