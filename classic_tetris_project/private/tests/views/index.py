from classic_tetris_project.test_helper import *

class Index(Spec):
    def test_renders(self):
        response = self.client.get("/")

        assert_that(response.status_code, equal_to(200))
