from classic_tetris_project.tests.helper import *
from classic_tetris_project.queue import Queue

class ChallengeCommandTestCase(CommandTestCase):
    # HELPERS
    @lazy
    def user1(self):
        return self.twitch_client.create_user(username="user1")

    @lazy
    def user2(self):
        return self.twitch_client.create_user(username="user2")

    def open_queue(self):
        Queue(self.twitch_channel.name).open()

    def patches(self):
        return super().patches() + [
            patch.object(twitch.APIClient, "user_from_username",
                         lambda _self, username, _client=None: self.twitch_client._username_cache.get(username))
        ]

    # TESTS
    def test_with_no_queue(self):
        self.assertTwitch("!challenge user1", [
            "The queue is not open."
        ])

    def test_with_invalid_user(self):
        self.open_queue()

        self.assertTwitch("!challenge user1", [
            "Twitch user \"user1\" does not exist."
        ])

    def test_with_own_user(self):
        self.open_queue()

        self.assertTwitch(f"!challenge {self.twitch_user.username}", [
            "You can't challenge yourself, silly!"
        ])

    def test_successful_challenge(self):
        self.user1
        self.open_queue()

        self.assertTwitch(f"!challenge user1", [
            f"@user1 : {self.twitch_user.username} has challenged you to a match on "
            f"twitch.tv/{self.twitch_channel.name}! You have 60 seconds to !accept or !decline."
        ])

    def test_with_existing_own_challenge(self):
        self.user1
        self.user2
        self.open_queue()
        self.send_twitch("!challenge user2")

        self.assertTwitch(f"!challenge user1", [
            "You have already challenged user2."
        ])

    def test_with_existing_other_challenge(self):
        self.user1
        self.open_queue()
        self.send_twitch("!challenge user1", self.user2)

        self.assertTwitch(f"!challenge user1", [
            "user1 already has a pending challenge."
        ])
