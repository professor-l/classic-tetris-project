from classic_tetris_project.test_helper import *
from classic_tetris_project.commands.command import Command, CommandException

class Command_(Spec):
    class discord_user_from_username:
        def with_mention(self):
            discord_user = DiscordUserFactory(discord_id="1234")

            assert_that(Command.discord_user_from_username("<@1234>"), equal_to(discord_user))
            assert_that(Command.discord_user_from_username("<@1235>"), equal_to(None))

        @patch("classic_tetris_project.discord.get_guild")
        def with_username(self, get_guild):
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

            assert_that(Command.discord_user_from_username("joe shmoe", guild1), equal_to(joe))
            assert_that(calling(Command.discord_user_from_username).with_args("plain jane", guild1),
                        raises(CommandException))
            assert_that(Command.discord_user_from_username("plain jane", guild1, raise_invalid=False),
                        equal_to(None))
            assert_that(Command.discord_user_from_username("jumping jack", guild1), equal_to(None))

            assert_that(calling(Command.discord_user_from_username).with_args("joe shmoe", guild2),
                        raises(CommandException))
            assert_that(Command.discord_user_from_username("plain jane", guild2), equal_to(jane))
            assert_that(Command.discord_user_from_username("jumping jack", guild2), equal_to(None))

            assert_that(Command.discord_user_from_username("joe shmoe"), equal_to(joe))
            assert_that(calling(Command.discord_user_from_username).with_args("plain jane"),
                        raises(CommandException))
            assert_that(Command.discord_user_from_username("jumping jack"), equal_to(None))

        def with_username_and_discriminator(self):
            joe = DiscordUserFactory(discord_id="1234")
            jane = DiscordUserFactory(discord_id="1235")
            jack = DiscordUserFactory(discord_id="1236")

            guild = MockDiscordGuild(members=[
                MockDiscordAPIUserFactory(name="Joe", discriminator="0001", display_name="Joe Shmoe", id=joe.discord_id),
                MockDiscordAPIUserFactory(name="Joe", discriminator="0002", display_name="Jumping Jack", id=jack.discord_id),
                MockDiscordAPIUserFactory(name="Jane", display_name="Plain Jane", id=jane.discord_id),
            ])

            assert_that(Command.discord_user_from_username("Joe#0001", guild), equal_to(joe))
            assert_that(Command.discord_user_from_username("Joe#0002", guild), equal_to(jack))
            assert_that(calling(Command.discord_user_from_username).with_args("Joe#0003", guild),
                        raises(CommandException))
            assert_that(Command.discord_user_from_username("Joe#0003", guild, raise_invalid=False),
                        equal_to(None))

    class twitch_user_from_username:
        def invalid(self):
            assert_that(calling(Command.twitch_user_from_username).with_args("invalid username"),
                        raises(CommandException))
            assert_that(Command.twitch_user_from_username("invalid username", raise_invalid=False),
                        equal_to(None))

        def with_existing(self):
            twitch_user = TwitchUserFactory(username="dexfore")

            assert_that(Command.twitch_user_from_username("dexfore"), equal_to(twitch_user))
            assert_that(Command.twitch_user_from_username("@dexfore"), equal_to(twitch_user))
            assert_that(Command.twitch_user_from_username("dexfore", existing_only=False),
                        equal_to(twitch_user))
            assert_that(TwitchUser.objects.count(), equal_to(1))

        @patch.object(twitch.APIClient, "user_from_username",
                      lambda self, username, client=None: MockTwitchAPIUser.create(username=username))
        def without_existing(self):
            twitch_user = TwitchUserFactory(username="professor_l")

            assert_that(Command.twitch_user_from_username("dexfore"), equal_to(None))
            assert_that(TwitchUser.objects.count(), equal_to(1))
            new_twitch_user = Command.twitch_user_from_username("dexfore", existing_only=False)
            assert_that(new_twitch_user.username, equal_to("dexfore"))
            assert_that(TwitchUser.objects.count(), equal_to(2))
