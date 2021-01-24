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
                QualifierFactory(user=self.current_user, event=self.event)
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

            def test_renders_qualifier_list(self):
                qualifier1 = QualifierFactory(event=self.event, approved=None)
                qualifier2 = QualifierFactory(event=self.event, approved=True)
                qualifier3 = QualifierFactory(event=self.event, approved=False)
                response = self.get()

                assert_that(response.status_code, equal_to(200))
                assert_that(response, has_html(f".data-table .data-table__row a",
                                               text=qualifier1.user.display_name))
                assert_that(response, has_html(f".data-table .data-table__row a",
                                               text=qualifier2.user.display_name))
                assert_that(response, not_(has_html(f".data-table .data-table__row a",
                                                    text=qualifier3.user.display_name)))



        class logged_out:
            def test_renders_logged_out(self):
                response = self.get({ "next": "/profile/" })

                assert_that(response.status_code, equal_to(200))
                assert_that(response, uses_template("event/index.html"))
                assert_that(response, uses_template("event/ineligible_reasons/logged_out.html"))

class QualifyView(Spec):
    @lazy
    def event(self):
        return EventFactory(qualifying_open=True)
    @property
    def url(self):
        return f"/event/{self.event.slug}/qualify/"
    def setup(self):
        super().setup()
        self.sign_in()

    class GET:
        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.get()

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))

        def test_renders(self):
            DiscordUserFactory(user=self.current_user)
            TwitchUserFactory(user=self.current_user)
            response = self.get()

            assert_that(response.status_code, equal_to(200))
            assert_that(response, uses_template("event/qualify.html"))

    class POST:
        def test_with_qualifying_closed(self):
            self.event.qualifying_open = False
            self.event.save()
            response = self.post({ "vod": "https://twitch.tv/qual1", "score": 200000, "details": "Hi there" })

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))
            assert_that(Qualifier.objects.count(), equal_to(0))

        def test_submits_qualifier(self):
            DiscordUserFactory(user=self.current_user)
            TwitchUserFactory(user=self.current_user)
            response = self.post({ "vod": "https://twitch.tv/qual1", "score": 200000, "details": "Hi there" })

            assert_that(response, redirects_to(f"/event/{self.event.slug}/"))
            assert_that(Qualifier.objects.count(), equal_to(1))
            assert_that(Qualifier.objects.last(), has_properties(
                vod="https://twitch.tv/qual1",
                qualifying_score=200000,
                details="Hi there",
            ))
