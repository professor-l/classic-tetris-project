from classic_tetris_project.tests.helper import *

class UserViewTestCase(TestCase):
    def test_with_own_profile(self):
        self.sign_in()
        response = self.client.get(f"/user/{self.current_user.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user/show.html")
        self.assertHTML(response, "a[href='/profile/edit/']", "Edit")

    def test_with_other_profile_id(self):
        user = UserFactory()
        response = self.client.get(f"/user/{user.id}/")

        self.assertEqual(response.status_code, 200)

    def test_with_other_profile_username(self):
        user = UserFactory()
        twitch_user = TwitchUserFactory(user=user, username="twitch_username")
        response = self.client.get(f"/user/{user.id}/")

        self.assertRedirects(response, "/user/twitch_username/")

        response = self.client.get(f"/user/twitch_username/")

        self.assertEqual(response.status_code, 200)

    def test_with_nonexistent_profile(self):
        response = self.client.get(f"/user/nonexistent_user/")
        self.assertEqual(response.status_code, 404)
