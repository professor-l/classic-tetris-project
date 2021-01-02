from classic_tetris_project.test_helper import *

class TestCommand_(CommandSpec):
    class discord:
        def sends_response(self):
            self.assert_discord("!test", [
                "Test!"
            ])

    class twitch:
        def sends_response(self):
            self.assert_twitch("!test", [
                "Test!"
            ])
