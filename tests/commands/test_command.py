from tests.helper import *
from classic_tetris_project.commands.command import Command, CommandException

class CommandTestCase(TestCase):
    with describe(".discord_user_from_username"):
        def test_discord_user_from_username_with_mention(self):
            discord_user = DiscordUserFactory(discord_id="1234")

            expect(Command.discord_user_from_username("<@1234>")).to(equal(discord_user))
            expect(Command.discord_user_from_username("<@1235>")).to(equal(None))

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

            expect(Command.discord_user_from_username("joe shmoe", guild1)).to(equal(joe))
            expect(lambda: Command.discord_user_from_username("plain jane", guild1)).to(raise_error(CommandException))
            expect(Command.discord_user_from_username("plain jane", guild1, raise_invalid=False)).to(equal(None))
            expect(Command.discord_user_from_username("jumping jack", guild1)).to(equal(None))

            expect(lambda: Command.discord_user_from_username("joe shmoe", guild2)).to(raise_error(CommandException))
            expect(Command.discord_user_from_username("plain jane", guild2)).to(equal(jane))
            expect(Command.discord_user_from_username("jumping jack", guild2)).to(equal(None))

            expect(Command.discord_user_from_username("joe shmoe")).to(equal(joe))
            expect(lambda: Command.discord_user_from_username("plain jane")).to(raise_error(CommandException))
            expect(Command.discord_user_from_username("jumping jack")).to(equal(None))

        def test_discord_user_from_username_with_username_and_discriminator(self):
            joe = DiscordUserFactory(discord_id="1234")
            jane = DiscordUserFactory(discord_id="1235")
            jack = DiscordUserFactory(discord_id="1236")

            guild = MockDiscordGuild(members=[
                MockDiscordAPIUserFactory(name="Joe", discriminator="0001", display_name="Joe Shmoe", id=joe.discord_id),
                MockDiscordAPIUserFactory(name="Joe", discriminator="0002", display_name="Jumping Jack", id=jack.discord_id),
                MockDiscordAPIUserFactory(name="Jane", display_name="Plain Jane", id=jane.discord_id),
            ])

            expect(Command.discord_user_from_username("Joe#0001", guild)).to(equal(joe))
            expect(Command.discord_user_from_username("Joe#0002", guild)).to(equal(jack))
            expect(lambda: Command.discord_user_from_username("Joe#0003", guild)).to(raise_error(CommandException))
            expect(Command.discord_user_from_username("Joe#0003", guild, raise_invalid=False)).to(equal(None))
