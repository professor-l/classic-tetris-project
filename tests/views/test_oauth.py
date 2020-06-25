from classic_tetris_project.tests.helper import *


class LoginTestCase(TestCase):
    url = "/oauth/login/"

    def test_renders(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "oauth/login.html")
        self.assertHTML(response, "a[href='/oauth/login/discord/']")
        self.assertHTML(response, "a[href='/oauth/login/twitch/']")

    def test_renders_with_next_path(self):
        response = self.get({ "next": "/profile/" })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "oauth/login.html")
        self.assertHTML(response, "a[href='/oauth/login/discord/?next=%2Fprofile%2F']")
        self.assertHTML(response, "a[href='/oauth/login/twitch/?next=%2Fprofile%2F']")


class LogoutTestCase(TestCase):
    url = "/oauth/logout/"

    def test_redirects_when_logged_in(self):
        self.sign_in()
        response = self.get()

        self.assertRedirects(response, "/")

    def test_redirects_when_logged_out(self):
        response = self.get()

        self.assertRedirects(response, "/")
