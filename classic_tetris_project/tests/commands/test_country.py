from classic_tetris_project.tests.helper import *

class GetCountryCommandTestCase(CommandTestCase):
    def test_discord_with_own_user_and_no_country(self):
        self.assertDiscord("!country", [
            "User has not set a country."
        ])

    def test_discord_with_own_user_and_country(self):
        self.discord_user.user.set_country("us")
        self.assertDiscord("!country", [
            f"{self.discord_api_user.name} is from United States!"
        ])

    def test_discord_with_other_user_and_no_country(self):
        discord_user = DiscordUserFactory(username="Other User")
        self.assertDiscord("!country Other User", [
            "User has not set a country."
        ])

    def test_discord_with_other_user_and_country(self):
        discord_user = DiscordUserFactory(username="Other User")
        discord_user.user.set_country("us")
        self.assertDiscord("!country Other User", [
            "Other User is from United States!"
        ])
