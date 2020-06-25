from classic_tetris_project.tests.helper import *

class TestCommandTestCase(CommandTestCase):
    def test_discord_sends_response(self):
        self.assertDiscord("!test", [
            "Test!"
        ])

    def test_twitch_sends_response(self):
        self.assertTwitch("!test", [
            "Test!"
        ])
