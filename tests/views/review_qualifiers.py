from classic_tetris_project.test_helper import *

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from classic_tetris_project.facades.user_permissions import UserPermissions

def add_review_permission(auth_user):
    content_type = ContentType.objects.get_for_model(Qualifier)
    permission = Permission.objects.get(
        codename='change_qualifier',
        content_type=content_type,
    )
    auth_user.user_permissions.add(permission)


class IndexView_(Spec):
    url = "/review_qualifiers/"

    def setup(self):
        super().setup()
        self.sign_in()

    class GET:
        class without_permission:
            def test_returns_403(self):
                response = self.get()

                assert_that(response.status_code, equal_to(403))

        class with_permission:
            def setup(self):
                super().setup()
                add_review_permission(self.current_auth_user)

            def test_renders_no_qualifiers(self):
                QualifierFactory(approved=True)

                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("review_qualifiers/index.html"))
                assert_that(response, not_(has_html("table.data-table")))

            def test_renders_qualifiers(self):
                QualifierFactory(approved=None)

                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("review_qualifiers/index.html"))
                assert_that(response, has_html("table.data-table"))

class ReviewView_(Spec):
    @lazy
    def qualifier(self):
        return QualifierFactory()
    @property
    def url(self):
        return f"/review_qualifiers/{self.qualifier.id}/"

    def setup(self):
        super().setup()
        self.sign_in()

    class GET:
        class without_permission:
            def test_returns_403(self):
                response = self.get()

                assert_that(response.status_code, equal_to(403))

        class with_permission:
            def setup(self):
                super().setup()
                add_review_permission(self.current_auth_user)

            def test_renders_already_reviewed(self):
                self.qualifier.approved = True
                self.qualifier.save()

                response = self.get()

                assert_that(response, redirects_to("/review_qualifiers/"))

            def test_without_qualifier(self):
                response = self.client.get("/review_qualifiers/-1/")

                assert_that(response.status_code, equal_to(404))

            def test_with_qualifier(self):
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("review_qualifiers/review.html"))

    class POST:
        class without_permission:
            def test_returns_403(self):
                response = self.post({ "approved": True })

                assert_that(response.status_code, equal_to(403))
                self.qualifier.refresh_from_db()
                assert_that(self.qualifier.approved, equal_to(None))

        class with_permission:
            def setup(self):
                super().setup()
                add_review_permission(self.current_auth_user)

            def test_renders_already_reviewed(self):
                self.qualifier.approved = False
                self.qualifier.save()

                response = self.post({ "approved": True })

                assert_that(response, redirects_to("/review_qualifiers/"))
                self.qualifier.refresh_from_db()
                assert_that(self.qualifier.approved, equal_to(False))

            def test_without_qualifier(self):
                response = self.client.post("/review_qualifiers/-1/", { "approved": True })

                assert_that(response.status_code, equal_to(404))

            @patch("classic_tetris_project.tasks.report_reviewed_qualifier.delay")
            def test_with_qualifier(self, _):
                response = self.post({
                    "approved": True, 
                    "notes": "Great job",
                    "announced": True,
                    "stencil": True,
                    "rom": True,
                    "timer": True,
                    "reset": True,
                })

                assert_that(response, redirects_to("/review_qualifiers/"))
                self.qualifier.refresh_from_db()
                assert_that(self.qualifier, has_properties(
                    approved=True,
                    reviewed_by=self.current_user,
                    review_data={
                        "notes": "Great job",
                        "checks": {
                            "announced": True,
                            "stencil": True,
                            "rom": True,
                            "timer": True,
                            "reset": True,
                        },
                    }
                ))
