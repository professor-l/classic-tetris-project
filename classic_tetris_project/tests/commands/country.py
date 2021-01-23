from classic_tetris_project.test_helper import *

class GetCountryCommand_(CommandSpec):
    class discord:
        def test_with_own_user_and_no_country(self):
            self.assert_discord("!country", [
                "User has not set a country."
            ])

        def test_with_own_user_and_country(self):
            self.discord_user.user.set_country("us")
            self.assert_discord("!country", [
                f"{self.discord_api_user.name} is from United States!"
            ])

        def test_with_other_user_and_no_country(self):
            discord_user = DiscordUserFactory(username="Other User")
            self.assert_discord("!country Other User", [
                "User has not set a country."
            ])

        def test_with_other_user_and_country(self):
            discord_user = DiscordUserFactory(username="Other User")
            discord_user.user.set_country("us")
            self.assert_discord("!country Other User", [
                "Other User is from United States!"
            ])
