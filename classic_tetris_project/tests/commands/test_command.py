from classic_tetris_project.tests.helper import *
from classic_tetris_project.commands.command import Command, CommandException

class CommandTestCase(TestCase):
    with describe(".discord_user_from_username"):
        def test_discord_user_from_username_with_mention(self):
            discord_user = DiscordUserFactory(discord_id="1234")

            self.assertEqual(Command.discord_user_from_username("<@1234>"), discord_user)
            self.assertEqual(Command.discord_user_from_username("<@1235>"), None)

        @patch("classic_tetris_project.discord.get_guild")
        def test_discord_user_from_username_with_username(self, get_guild):
            joe = DiscordUserFactory(discord_id="1234")
            jane = DiscordUserFactory(discord_id="1235")

            guild1 = MockDiscordGuild(members=[
                MockDiscordAPIUserFactory(name="Joe", display_name="Joe Shmoe", id=joe.discord_id),
                MockDiscordAPIUserFactory(name="Jack", display_name="Jumping Jack"),
            ])
            guild2 = MockDiscordGuild(members=[
                MockDiscordAPIUserFactory(name="Jane", display_name="Plain Jane", id=jane.discord_id),
                MockDiscordAPIUserFactory(name="Jack", display_name="Jumping Jack"),
            ])
            get_guild.return_value = guild1

            self.assertEqual(Command.discord_user_from_username("joe shmoe", guild1), joe)
            with self.assertRaises(CommandException):
                Command.discord_user_from_username("plain jane", guild1)
            self.assertEqual(Command.discord_user_from_username("plain jane", guild1,
                                                                raise_invalid=False), None)
            self.assertEqual(Command.discord_user_from_username("jumping jack", guild1), None)

            with self.assertRaises(CommandException):
                Command.discord_user_from_username("joe shmoe", guild2)
            self.assertEqual(Command.discord_user_from_username("plain jane", guild2), jane)
            self.assertEqual(Command.discord_user_from_username("jumping jack", guild2), None)

            self.assertEqual(Command.discord_user_from_username("joe shmoe"), joe)
            with self.assertRaises(CommandException):
                Command.discord_user_from_username("plain jane")
            self.assertEqual(Command.discord_user_from_username("jumping jack"), None)

        def test_discord_user_from_username_with_username_and_discriminator(self):
            joe = DiscordUserFactory(discord_id="1234")
            jane = DiscordUserFactory(discord_id="1235")
            jack = DiscordUserFactory(discord_id="1236")

            guild = MockDiscordGuild(members=[
                MockDiscordAPIUserFactory(name="Joe", discriminator="0001", display_name="Joe Shmoe", id=joe.discord_id),
                MockDiscordAPIUserFactory(name="Joe", discriminator="0002", display_name="Jumping Jack", id=jack.discord_id),
                MockDiscordAPIUserFactory(name="Jane", display_name="Plain Jane", id=jane.discord_id),
            ])

            self.assertEqual(Command.discord_user_from_username("Joe#0001", guild), joe)
            self.assertEqual(Command.discord_user_from_username("Joe#0002", guild), jack)
            with self.assertRaises(CommandException):
                Command.discord_user_from_username("Joe#0003", guild)
            self.assertEqual(Command.discord_user_from_username("Joe#0003", guild,
                                                                raise_invalid=False), None)

    with describe(".twitch_user_from_username"):
        def test_twitch_user_from_username_invalid(self):
            with self.assertRaises(CommandException):
                Command.twitch_user_from_username("invalid username")
            self.assertEqual(Command.twitch_user_from_username("invalid username",
                                                               raise_invalid=False), None)

        def test_twitch_user_from_username_with_existing(self):
            twitch_user = TwitchUserFactory(username="dexfore")

            self.assertEqual(Command.twitch_user_from_username("dexfore"), twitch_user)
            self.assertEqual(Command.twitch_user_from_username("@dexfore"), twitch_user)
            self.assertEqual(Command.twitch_user_from_username("dexfore", existing_only=False), twitch_user)
            self.assertEqual(TwitchUser.objects.count(), 1)

        @patch.object(twitch.APIClient, "user_from_username",
                      lambda self, username, client=None: MockTwitchAPIUser.create(username=username))
        def test_twitch_user_from_username_without_existing(self):
            twitch_user = TwitchUserFactory(username="professor_l")

            self.assertEqual(Command.twitch_user_from_username("dexfore"), None)
            self.assertEqual(TwitchUser.objects.count(), 1)
            new_twitch_user = Command.twitch_user_from_username("dexfore", existing_only=False)
            self.assertEqual(new_twitch_user.username, "dexfore")
            self.assertEqual(TwitchUser.objects.count(), 2)
