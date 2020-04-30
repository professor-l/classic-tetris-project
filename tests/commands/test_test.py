from ..helper import *

class TestCommandTestCase(CommandTestCase):
    def test_discord_sends_response(self):
        self.expect_discord("!test", [
            "Test!"
        ])

    def test_twitch_sends_response(self):
        self.expect_twitch("!test", [
            "Test!"
        ])
