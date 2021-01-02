from classic_tetris_project.test_helper import *


class Login(Spec):
    url = "/oauth/login/"

    def renders(self):
        response = self.get()

        assert_that(response.status_code, equal_to(200))
        assert_that(response, uses_template("oauth/login.html"))
        assert_that(response, has_html("a[href='/oauth/login/discord/']"))
        assert_that(response, has_html("a[href='/oauth/login/twitch/']")) 

    def renders_with_next_path(self):
        response = self.get({ "next": "/profile/" })

        assert_that(response.status_code, equal_to(200))
        assert_that(response, uses_template("oauth/login.html"))
        assert_that(response, has_html("a[href='/oauth/login/discord/?next=%2Fprofile%2F']"))
        assert_that(response, has_html("a[href='/oauth/login/twitch/?next=%2Fprofile%2F']"))


class Logout(Spec):
    url = "/oauth/logout/"

    def redirects_when_logged_in(self):
        self.sign_in()
        response = self.get()

        assert_that(response, redirects_to("/"))

    def redirects_when_logged_out(self):
        response = self.get()

        assert_that(response, redirects_to("/"))
