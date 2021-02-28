from classic_tetris_project.test_helper import *


class QualifierView_(Spec):
    @property
    def url(self):
        return f"/qualifier/{self.qualifier.id}/"

    @lazy
    def event(self):
        return EventFactory(qualifying_open=True)

    @lazy
    def qualifier(self):
        return QualifierFactory(user=self.current_user, event=self.event, approved_=True)

    @lazy
    def other_qualifier(self):
        return QualifierFactory(event=self.event, approved_=True)

    def setup(self):
        super().setup()
        self.sign_in()

    class GET:
        def test_without_qualifier(self):
            response = self.client.get("/qualifier/-1/")

            assert_that(response.status_code, equal_to(404))

        def test_with_own_qualifier(self):
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, uses_template("qualifiers/show.html"))
            assert_that(response, has_html("input[value='Withdraw']"))

        def test_with_other_qualifier(self):
            response = self.client.get(f"/qualifier/{self.other_qualifier.id}/")

            assert_that(response.status_code, equal_to(200))
            assert_that(response, uses_template("qualifiers/show.html"))
            assert_that(response, not_(has_html("input[value='Withdraw']")))

        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, not_(has_html("input[value='Withdraw']")))

        def test_with_not_submitted(self):
            self.qualifier.approved = None
            self.qualifier.submitted = False
            self.qualifier.save()
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, not_(has_html("input[value='Withdraw']")))

        def test_with_already_withdrawn(self):
            self.qualifier.withdrawn = True
            self.qualifier.save()
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, not_(has_html("input[value='Withdraw']")))

    class POST:
        def test_without_qualifier(self):
            response = self.client.post("/qualifier/-1/", { "withdrawn": True })

            assert_that(response.status_code, equal_to(404))

        def test_withdraws(self):
            response = self.post({ "withdrawn": True })

            assert_that(response, redirects_to(f"/qualifier/{self.qualifier.id}/"))
            self.qualifier.refresh_from_db()
            assert_that(self.qualifier.withdrawn, equal_to(True))

        def test_with_other_qualifier(self):
            response = self.client.post(f"/qualifier/{self.other_qualifier.id}/", { "withdrawn": True })

            assert_that(response.status_code, equal_to(403))
            self.other_qualifier.refresh_from_db()
            assert_that(self.other_qualifier.withdrawn, equal_to(False))

        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.post({ "withdrawn": True })

            assert_that(response.status_code, equal_to(403))
            self.qualifier.refresh_from_db()
            assert_that(self.qualifier.withdrawn, equal_to(False))

        def test_with_not_submitted(self):
            self.qualifier.approved = None
            self.qualifier.submitted = False
            self.qualifier.save()
            response = self.post({ "withdrawn": True })

            assert_that(response.status_code, equal_to(403))
            self.qualifier.refresh_from_db()
            assert_that(self.qualifier.withdrawn, equal_to(False))

        def test_with_already_withdrawn(self):
            self.qualifier.withdrawn = True
            self.qualifier.save()
            response = self.post({ "withdrawn": True })

            assert_that(response.status_code, equal_to(403))
            self.qualifier.refresh_from_db()
            assert_that(self.qualifier.withdrawn, equal_to(True))
