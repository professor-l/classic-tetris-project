from classic_tetris_project.test_helper import *

class UserView_(Spec):
    def test_with_own_profile(self):
        self.sign_in()
        response = self.client.get(f"/user/{self.current_user.id}/")

        assert_that(response.status_code, equal_to(200))
        assert_that(response, uses_template("user/show.html"))
        assert_that(response, has_html("a[href='/profile/edit/']", "Edit"))

    def test_with_other_profile_id(self):
        user = UserFactory()
        response = self.client.get(f"/user/{user.id}/")

        assert_that(response.status_code, equal_to(200))

    def test_with_other_profile_username(self):
        user = UserFactory()
        twitch_user = TwitchUserFactory(user=user, username="twitch_username")
        response = self.client.get(f"/user/{user.id}/")

        assert_that(response, redirects_to("/user/twitch_username/"))

        response = self.client.get(f"/user/twitch_username/")

        assert_that(response.status_code, equal_to(200))

    def test_with_nonexistent_profile(self):
        response = self.client.get(f"/user/nonexistent_user/")
        assert_that(response.status_code, equal_to(404))
