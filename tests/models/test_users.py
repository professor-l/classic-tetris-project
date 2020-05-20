from tests.helper import *

from classic_tetris_project import discord
patch.object(discord.APIClient, "_request", side_effect=Exception("discord API called")).start()

class UserTestCase(TestCase):
    @lazy
    def user(self):
        return UserFactory()

    @lazy
    def other_user(self):
        return UserFactory()


    with describe("#add_pb"):
        def test_add_pb_creates_score_pb(self):
            expect(ScorePB.objects.count()).to(equal(0))

            self.user.add_pb(200000)

            expect(ScorePB.objects.count()).to(equal(1))
            score_pb = ScorePB.objects.last()
            expect(score_pb.user).to(equal(self.user))
            expect(score_pb.current).to(equal(True))
            expect(score_pb.score).to(equal(200000))
            expect(score_pb.console_type).to(equal("ntsc"))
            expect(score_pb.starting_level).to(equal(None))
            expect(score_pb.lines).to(equal(None))

        def test_add_pb_with_params_creates_score_pb(self):
            expect(ScorePB.objects.count()).to(equal(0))

            self.user.add_pb(200000, console_type="pal", starting_level=18, lines=30)

            expect(ScorePB.objects.count()).to(equal(1))
            score_pb = ScorePB.objects.last()
            expect(score_pb.user).to(equal(self.user))
            expect(score_pb.current).to(equal(True))
            expect(score_pb.score).to(equal(200000))
            expect(score_pb.console_type).to(equal("pal"))
            expect(score_pb.starting_level).to(equal(18))
            expect(score_pb.lines).to(equal(30))

        def test_add_pb_with_existing_replaces_current(self):
            score_pb_other = ScorePBFactory()
            score_pb_pal = ScorePBFactory(user=self.user, console_type="pal")
            score_pb_19 = ScorePBFactory(user=self.user, starting_level=19)
            score_pb = ScorePBFactory(user=self.user)

            self.user.add_pb(200000)
            score_pb_other.refresh_from_db()
            score_pb_pal.refresh_from_db()
            score_pb_19.refresh_from_db()
            score_pb.refresh_from_db()

            expect(score_pb_other.current).to(equal(True))
            expect(score_pb_pal.current).to(equal(True))
            expect(score_pb_19.current).to(equal(True))
            expect(score_pb.current).to(equal(False))


    with describe("#get_pb"):
        def test_get_pb_without_score_pbs_returns_none(self):
            score_pb_other = self.other_user.add_pb(999999)

            expect(self.user.get_pb()).to(equal(None))

        def test_get_pb_returns_greatest_score(self):
            score_pb_other = self.other_user.add_pb(999999)

            score_pb_accident = self.user.add_pb(2000000)
            score_pb_old = self.user.add_pb(200000)
            score_pb_18_old = self.user.add_pb(200000, starting_level=18)
            score_pb_18 = self.user.add_pb(400000, starting_level=18)
            score_pb_19 = self.user.add_pb(300000, starting_level=19)
            score_pb_pal_old = self.user.add_pb(300000, console_type="pal")
            score_pb_pal = self.user.add_pb(500000, console_type="pal")

            expect(self.user.get_pb()).to(equal(400000))
            expect(self.user.get_pb(starting_level=18)).to(equal(400000))
            expect(self.user.get_pb(starting_level=19)).to(equal(300000))
            expect(self.user.get_pb(console_type="pal")).to(equal(500000))


class DiscordUserTestCase(TestCase):
    @lazy
    def discord_user(self):
        return DiscordUserFactory(discord_id="1001", username="User 1", discriminator="9001")

    @lazy
    def discord_user_old(self):
        return DiscordUserFactory(discord_id="1001", username="User 1 old", discriminator="8001")

    @lazy
    def discord_user_other(self):
        return DiscordUserFactory(discord_id="1002", username="User 2", discriminator="9002")

    @lazy
    def user_obj(self):
        return discord.wrap_user_dict({ "id": "1001", "username": "User 1", "discriminator": "9001",
                                       "avatar": "1001" })

    with describe(".get_or_create_from_user_obj"):
        def test_get_or_create_from_user_obj_returns_existing_user(self):
            existing_discord_user = self.discord_user
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            expect(discord_user).to(equal(existing_discord_user))

        def test_get_or_create_from_user_obj_updates_existing_user(self):
            existing_discord_user = self.discord_user_old
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            expect(discord_user).to(equal(existing_discord_user))
            existing_discord_user.refresh_from_db()
            expect(existing_discord_user.username).to(equal("User 1"))
            expect(existing_discord_user.discriminator).to(equal("9001"))

        def test_get_or_create_from_user_obj_creates_user(self):
            discord_user = DiscordUser.get_or_create_from_user_obj(self.user_obj)

            expect(DiscordUser.objects.count()).to(equal(1))
            expect(discord_user.discord_id).to(equal("1001"))
            expect(discord_user.username).to(equal("User 1"))
            expect(discord_user.discriminator).to(equal("9001"))

    with describe("#update_fields"):
        def test_update_fields_updates_fields(self):
            self.discord_user_old.update_fields(self.user_obj)

            self.discord_user_old.refresh_from_db()
            expect(self.discord_user_old.username).to(equal("User 1"))
            expect(self.discord_user_old.discriminator).to(equal("9001"))

        def test_update_fields_doesnt_save_if_no_change(self):
            self.discord_user
            with patch.object(DiscordUser, "save") as save:
                self.discord_user.update_fields(self.user_obj)

            expect(self.discord_user.username).to(equal("User 1"))
            expect(self.discord_user.discriminator).to(equal("9001"))
            save.assert_not_called()

        def test_update_fields_complains_given_wrong_id(self):
            expect(lambda: self.discord_user_other.update_fields(self.user_obj)).to(raise_error)
