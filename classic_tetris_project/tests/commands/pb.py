from classic_tetris_project.test_helper import *

class GetPBCommand_(CommandSpec):
    class discord:
        def test_with_no_user(self):
            self.assert_discord("!pb", [
                "User has not set a PB."
            ])

        def test_with_no_pb(self):
            self.discord_user

            self.assert_discord("!pb", [
                "User has not set a PB."
            ])

        def test_with_ntsc_pb(self):
            self.discord_user.user.add_pb(100000)

            self.assert_discord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 100,000."
            ])

        def test_with_ntsc_18_and_19_pb(self):
            self.discord_user.user.add_pb(600000, starting_level=18)
            self.discord_user.user.add_pb(100000, starting_level=19)

            self.assert_discord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 600,000 (100,000 19 start)."
            ])

        def test_with_pal_pb(self):
            self.discord_user.user.add_pb(100000, console_type="pal")

            self.assert_discord("!pb", [
                f"{self.discord_api_user.name} has a PAL PB of 100,000."
            ])

        def test_with_ntsc_and_pal_pb(self):
            self.discord_user.user.add_pb(200000, console_type="ntsc")
            self.discord_user.user.add_pb(100000, console_type="pal")

            self.assert_discord("!pb", [
                f"{self.discord_api_user.name} has an NTSC PB of 200,000 and a PAL PB of 100,000."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username",
               return_value=None)
        def test_with_nonexistent_user(self, _):
            self.assert_discord("!pb Other User", [
                "User has not set a PB."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_with_user_with_no_pb(self, any_platform_user_from_username):
            discord_user = DiscordUserFactory(username="Other User")
            any_platform_user_from_username.return_value = discord_user

            self.assert_discord("!pb Other User", [
                "User has not set a PB."
            ])

            any_platform_user_from_username.assert_called_once_with("Other User")

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_with_user_with_pb(self, any_platform_user_from_username):
            discord_user = DiscordUserFactory(username="Other User")
            discord_user.user.add_pb(100000)
            any_platform_user_from_username.return_value = discord_user

            self.assert_discord("!pb Other User", [
                "Other User has an NTSC PB of 100,000."
            ])

            any_platform_user_from_username.assert_called_once_with("Other User")

    class twitch:
        @patch.object(twitch.APIClient, "user_from_id",
                      lambda self, user_id, client=None: MockTwitchAPIUser.create(id=user_id))
        def test_with_no_user(self):
            self.assert_twitch("!pb", [
                "User has not set a PB."
            ])

        def test_with_no_pb(self):
            self.twitch_user

            self.assert_twitch("!pb", [
                "User has not set a PB."
            ])

        def test_with_ntsc_pb(self):
            self.twitch_user.user.add_pb(100000)

            self.assert_twitch("!pb", [
                f"{self.twitch_api_user.username} has an NTSC PB of 100,000."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username",
               return_value=None)
        def test_with_nonexistent_user(self, _):
            self.assert_twitch("!pb other_user", [
                "User has not set a PB."
            ])

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_with_user_with_no_pb(self, any_platform_user_from_username):
            twitch_user = TwitchUserFactory(username="other_user")
            any_platform_user_from_username.return_value = twitch_user

            self.assert_twitch("!pb other_user", [
                "User has not set a PB."
            ])

            any_platform_user_from_username.assert_called_once_with("other_user")

        @patch("classic_tetris_project.commands.command.Command.any_platform_user_from_username")
        def test_with_user_with_pb(self, any_platform_user_from_username):
            twitch_user = TwitchUserFactory(username="other_user")
            twitch_user.user.add_pb(100000)
            any_platform_user_from_username.return_value = twitch_user

            self.assert_twitch("!pb other_user", [
                "other_user has an NTSC PB of 100,000."
            ])

            any_platform_user_from_username.assert_called_once_with("other_user")


class SetPBCommand_(CommandSpec):
    class discord:
        def test_with_no_args(self):
            self.assert_discord("!setpb", [re.compile("^Usage:")])

        def test_with_no_user(self):
            self.assert_discord("!setpb 100,000", [
                f"<@{self.discord_api_user.id}> has a new NTSC PB of 100,000!"
            ])

            assert_that(User.objects.count(), equal_to(1))
            assert_that(ScorePB.objects.count(), equal_to(1))
            user = User.objects.last()
            assert_that(user.get_pb(), equal_to(100000))

        def test_with_user(self):
            self.discord_user

            self.assert_discord("!setpb 100000", [
                f"<@{self.discord_api_user.id}> has a new NTSC PB of 100,000!"
            ])

            assert_that(User.objects.count(), equal_to(1))
            assert_that(ScorePB.objects.count(), equal_to(1))
            assert_that(self.discord_user.user.get_pb(), equal_to(100000))

        def test_level(self):
            self.assert_discord("!setpb 100000 NTSC 19", [
                f"<@{self.discord_api_user.id}> has a new NTSC level 19 PB of 100,000!"
            ])

            assert_that(ScorePB.objects.count(), equal_to(1))
            assert_that(User.objects.last().get_pb(console_type="ntsc", starting_level=19),
                        equal_to(100000))

        def test_pal(self):
            self.assert_discord("!setpb 100000 PAL", [
                f"<@{self.discord_api_user.id}> has a new PAL PB of 100,000!"
            ])

            assert_that(ScorePB.objects.count(), equal_to(1))
            assert_that(User.objects.last().get_pb(console_type="pal"), equal_to(100000))

        def test_errors(self):
            self.assert_discord("!setpb asdf", [re.compile("^Usage:")])
            self.assert_discord("!setpb -5", ["Invalid PB."])
            self.assert_discord("!setpb 1600000", ["You wish, kid >.>"])
            self.assert_discord("!setpb 100000 NTSC -5", ["Invalid level."])
            self.assert_discord("!setpb 100000 NTSC 30", ["Invalid level."])
            self.assert_discord("!setpb 100000 foo", [re.compile("^Invalid PB type")])

    class twitch:
        def test_with_no_args(self):
            self.assert_twitch("!setpb", [re.compile("Usage:")])

        @patch.object(twitch.APIClient, "user_from_id",
                      lambda self, user_id, client=None: MockTwitchAPIUser.create(id=user_id))
        def test_with_no_user(self):
            self.twitch_channel
            assert_that(User.objects.count(), equal_to(1))

            self.assert_twitch("!setpb 100,000", [
                f"@{self.twitch_api_user.username} has a new NTSC PB of 100,000!"
            ])

            assert_that(User.objects.count(), equal_to(2))
            assert_that(ScorePB.objects.count(), equal_to(1))
            user = User.objects.last()
            assert_that(user.get_pb(), equal_to(100000))

        def test_with_user(self):
            self.twitch_channel
            self.twitch_user
            assert_that(User.objects.count(), equal_to(2))

            self.assert_twitch("!setpb 100000", [
                f"@{self.twitch_api_user.username} has a new NTSC PB of 100,000!"
            ])

            assert_that(User.objects.count(), equal_to(2))
            assert_that(ScorePB.objects.count(), equal_to(1))
            assert_that(self.twitch_user.user.get_pb(), equal_to(100000))
