from classic_tetris_project.tests.helper import *


class ProfileViewTestCase(TestCase):
    url = "/profile/"
    def test_redirects_when_logged_in(self):
        self.sign_in()
        response = self.get()

        self.assertRedirects(response, f"/user/{self.current_user.id}/")

    def test_redirects_when_logged_out(self):
        response = self.get()

        self.assertRedirects(response, f"/oauth/login/?next=/profile/")


class ProfileEditViewTestCase(TestCase):
    url = "/profile/edit/"
    with describe("#get"):
        def test_get_redirects_when_logged_out(self):
            response = self.get()

            self.assertRedirects(response, f"/oauth/login/?next=/profile/edit/")

        def test_get_renders(self):
            self.sign_in()
            response = self.get()

            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "profile/edit.html")

    with describe("#post"):
        def test_post_redirects_when_logged_out(self):
            response = self.post()

            self.assertRedirects(response, f"/oauth/login/?next=/profile/edit/")

        def test_post_updates_and_redirects(self):
            self.sign_in()
            response = self.post({
                "preferred_name": "Preferred Name",
                "pronouns": "he",
                "country": "us",
                "playstyle": "das",
                "id": -1,
            })

            self.assertRedirects(response, f"/user/{self.current_user.id}/")
            self.current_user.refresh_from_db()
            self.assertEqual(self.current_user.preferred_name, "Preferred Name")
            self.assertEqual(self.current_user.pronouns, "he")
            self.assertEqual(self.current_user.country, "us")
            self.assertEqual(self.current_user.playstyle, "das")
            self.assertNotEqual(self.current_user.id, -1)
