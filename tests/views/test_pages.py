from classic_tetris_project.tests.helper import *

class PagesTestCase(TestCase):
    def test_invalid_page(self):
        response = self.client.get(f"/page/foo/")

        self.assertEqual(response.status_code, 404)

    def test_private_page(self):
        PageFactory(slug="foo", public=False)
        response = self.client.get(f"/page/foo/")

        self.assertEqual(response.status_code, 404)

    def test_public_page(self):
        PageFactory(slug="foo", public=True, content="This is the page body")
        response = self.client.get(f"/page/foo/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/page.html')
        self.assertContains(response, "This is the page body")
