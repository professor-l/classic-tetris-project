from classic_tetris_project.test_helper import *


class ProfileView_(Spec):
    url = "/profile/"
    def test_redirects_when_logged_in(self):
        self.sign_in()
        response = self.get()

        assert_that(response, redirects_to(f"/user/{self.current_user.id}/"))

    def test_redirects_when_logged_out(self):
        response = self.get()

        assert_that(response, redirects_to(f"/oauth/login/?next=/profile/"))


class ProfileEditView_(Spec):
    url = "/profile/edit/"
    class GET:
        def test_redirects_when_logged_out(self):
            response = self.get()

            assert_that(response, redirects_to(f"/oauth/login/?next=/profile/edit/"))

        def test_renders(self):
            self.sign_in()
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, uses_template("profile/edit.haml"))

    class POST:
        def test_redirects_when_logged_out(self):
            response = self.post()

            assert_that(response, redirects_to(f"/oauth/login/?next=/profile/edit/"))

        def test_updates_and_redirects(self):
            self.sign_in()
            response = self.post({
                "preferred_name": "Preferred Name",
                "pronouns": "he",
                "country": "us",
                "playstyle": "das",
                "id": -1,
            })

            assert_that(response, redirects_to(f"/user/{self.current_user.id}/"))
            self.current_user.refresh_from_db()
            assert_that(self.current_user, has_properties(
                preferred_name=equal_to("Preferred Name"),
                pronouns=equal_to("he"),
                country=equal_to("us"),
                playstyle=equal_to("das"),
                id=not_(equal_to(-1))
            ))
