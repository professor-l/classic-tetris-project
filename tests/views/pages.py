from classic_tetris_project.test_helper import *

class Pages(Spec):
    def test_invalid_page(self):
        response = self.client.get(f"/page/foo/")

        assert_that(response.status_code, equal_to(404))

    def test_private_page(self):
        PageFactory(slug="foo", public=False)
        response = self.client.get(f"/page/foo/")

        assert_that(response.status_code, equal_to(404))

    def test_public_page(self):
        PageFactory(slug="foo", public=True, content="This is the page body")
        response = self.client.get(f"/page/foo/")

        assert_that(response.status_code, equal_to(200))
        assert_that(response, uses_template("pages/page.html"))
        assert_that(str(response.content), contains_string("This is the page body"))
