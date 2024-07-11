from classic_tetris_project.test_helper import *

class IndexView_(Spec):
    @lazy
    def event(self):
        return EventFactory(qualifying_open=True)
    @property
    def url(self):
        return f"/event/{self.event.slug}/"

    class GET:
        class logged_in:
            def setup(self):
                super().setup()
                self.sign_in()

            def test_renders_closed(self):
                self.event.qualifying_open = False
                self.event.save()
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, uses_template("event/ineligible_reasons/closed.html"))

            def test_renders_already_qualified(self):
                QualifierFactory(user=self.current_user, event=self.event, submitted_=True)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, uses_template("event/ineligible_reasons/already_qualified.html"))

            def test_renders_link_twitch(self):
                DiscordUserFactory(user=self.current_user)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, uses_template("event/ineligible_reasons/link_twitch.html"))

            def test_renders_link_discord(self):
                TwitchUserFactory(user=self.current_user)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, uses_template("event/ineligible_reasons/link_discord.html"))

            def test_renders_qualify_button(self):
                DiscordUserFactory(user=self.current_user)
                TwitchUserFactory(user=self.current_user)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, has_html(f"a[href='/event/{self.event.slug}/qualify/']"))

            def test_renders_qualify_button_with_started_qualifier(self):
                DiscordUserFactory(user=self.current_user)
                TwitchUserFactory(user=self.current_user)
                QualifierFactory(user=self.current_user, event=self.event)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, has_html(f"a[href='/event/{self.event.slug}/qualify/']"))

            def test_renders_qualifier_list(self):
                qualifier1 = QualifierFactory(event=self.event, submitted_=True, approved=None)
                qualifier2 = QualifierFactory(event=self.event, submitted_=True, approved=True)
                qualifier3 = QualifierFactory(event=self.event, submitted_=True, approved=False)
                qualifier4 = QualifierFactory(event=self.event)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, has_html(f".data-table .data-table__row a",
                                               text=qualifier1.user.display_name))
                assert_that(response, has_html(f".data-table .data-table__row a",
                                               text=qualifier2.user.display_name))
                assert_that(response, not_(has_html(f".data-table .data-table__row a",
                                                    text=qualifier3.user.display_name)))
                assert_that(response, not_(has_html(f".data-table .data-table__row a",
                                                    text=qualifier4.user.display_name)))



        class logged_out:
            def test_renders_logged_out(self):
                response = self.get({ "next": "/profile/" })

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, uses_template("event/ineligible_reasons/logged_out.html"))


class QualifyView_(Spec):
    @lazy
    def event(self):
        return EventFactory(qualifying_open=True)
    @property
    def url(self):
        return f"/event/{self.event.slug}/qualify/"
    def setup(self):
        super().setup()
        self.sign_in()
        DiscordUserFactory(user=self.current_user)
        TwitchUserFactory(user=self.current_user)

    class GET:
        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.get()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))

        def test_with_qualifier_started(self):
            QualifierFactory(event=self.event, user=self.current_user)
            response = self.get()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/qualifier/"))

        def test_renders(self):
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, uses_template("event/qualify.html"))

    class POST:
        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.post()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))
            assert_that(Qualifier.objects.count(), equal_to(0))

        def test_with_qualifier_started(self):
            QualifierFactory(event=self.event, user=self.current_user)
            assert_that(Qualifier.objects.count(), equal_to(1))
            response = self.post()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/qualifier/"))
            assert_that(Qualifier.objects.count(), equal_to(1))

        @patch.object(Qualifier, "report_started")
        def test_creates_qualifier(self, report_started):
            assert_that(Qualifier.objects.count(), equal_to(0))
            response = self.post()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/qualifier/"))
            assert_that(Qualifier.objects.count(), equal_to(1))
            qualifier = Qualifier.objects.last()
            assert_that(qualifier, has_properties(
                user=self.current_user,
                event=self.event,
                submitted=False,
            ))
            report_started.assert_called_once()


class QualifierView_(Spec):
    @lazy
    def event(self):
        return EventFactory(qualifying_open=True)
    @lazy
    def qualifier(self):
        return QualifierFactory(event=self.event, user=self.current_user)
    @property
    def url(self):
        return f"/event/{self.event.slug}/qualifier/"
    def setup(self):
        super().setup()
        DiscordUserFactory(user=self.current_user)
        TwitchUserFactory(user=self.current_user)
        self.sign_in()
        self.qualifier

    class GET:
        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.get()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))

        def test_with_submitted_qualifier(self):
            self.qualifier.submitted = True
            self.qualifier.save()
            response = self.get()

            assert_that(response, redirects_to(f"/qualifier/{self.qualifier.id}/"))

        def test_without_qualifier(self):
            self.qualifier.delete()
            response = self.get()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/qualify/"))

        def test_renders(self):
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, uses_template("event/qualifier.haml"))

    class POST:
        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.post({ "vod": "https://twitch.tv/qual1", "score": 200000, "details": "Hi there" })

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))
            self.qualifier.refresh_from_db()
            assert_that(self.qualifier.submitted, equal_to(False))

        def test_without_qualifier(self):
            self.qualifier.delete()
            response = self.post({ "vod": "https://twitch.tv/qual1", "score": 200000, "details": "Hi there" })

            assert_that(response, redirects_to(f"/event/{self.event.slug}/qualify/"))

        @patch.object(Qualifier, "report_submitted")
        def test_submits_qualifier(self, report_submitted):
            response = self.post({ "vod": "https://twitch.tv/qual1", "score": 200000, "details": "Hi there" })

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))
            self.qualifier.refresh_from_db()
            assert_that(self.qualifier, has_properties(
                submitted=True,
                approved=None,
                vod="https://twitch.tv/qual1",
                qualifying_score=200000,
                details="Hi there",
            ))
            report_submitted.assert_called_once()
