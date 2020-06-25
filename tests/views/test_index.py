from classic_tetris_project.tests.helper import *

class IndexTestCase(TestCase):
    def test_renders(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
