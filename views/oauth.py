from django.contrib import auth, messages
from django.shortcuts import redirect, render
from django.urls import reverse
from furl import furl

from classic_tetris_project import discord, twitch
from classic_tetris_project.models import DiscordUser, TwitchUser, WebsiteUser
from classic_tetris_project.util.memo import lazy
from classic_tetris_project.util.merge import UserMerger
from .. import oauth
from .base import BaseView


def login(request):
    login_params = {}
    if "next" in request.GET:
        login_params["next"] = request.GET["next"]

    return render(request, "oauth/login.html", {
        "discord_path": furl(reverse("oauth:login", args=["discord"]), login_params).url,
        "twitch_path": furl(reverse("oauth:login", args=["twitch"]), login_params).url,
    })

def logout(request):
    auth.logout(request)
    return redirect(reverse("index"))


class OauthView(BaseView):
    @lazy
    def provider(self):
        return self.kwargs["provider"]

    @lazy
    def oauth(self):
        if self.provider == "discord":
            return oauth.discord
        elif self.provider == "twitch":
            return oauth.twitch


class LoginView(OauthView):
    def get(self, request, provider):
        if not self.oauth:
            return redirect(reverse("index"))

        state = oauth.State.from_request(request)
        redirect_uri = request.build_absolute_uri(reverse("oauth:authorize", args=[provider]))
        return self.oauth.authorize_redirect(request, redirect_uri, state=state.store())


class AuthorizeView(OauthView):
    def get(self, request, provider):
        if self.check_invalid_login():
            return redirect(reverse("index"))

        self.state.expire()

        token = self.oauth.authorize_access_token(request)
        platform_user = self.platform_user(token)
        self.merge_and_login(platform_user.user)

        return redirect(self.redirect_path())

    def merge_and_login(self, user):
        if self.state["merge_accounts"] and self.current_user:
            try:
                user = UserMerger(user, self.current_user).merge()
            except UserMerger.MergeError:
                messages.info(self.request, "Failed to link accounts, please contact a dev.")
                return
        website_user = WebsiteUser.fetch_by_user(user)
        auth.login(self.request, website_user.auth_user)

    def platform_user(self, token):
        if self.provider == "discord":
            return self.discord_user(token)
        elif self.provider == "twitch":
            return self.twitch_user(token)

    def discord_user(self, token):
        response = self.oauth.get("users/@me", token=token)
        user = discord.wrap_user_dict(response.json())
        return DiscordUser.get_or_create_from_user_obj(user)

    def twitch_user(self, token):
        # There's a way to add token endpoint auth methods to the OAuth client to satisfy Twitch's
        # requirements, but it's easier to just do this explicitly
        user_obj = twitch.API.own_user(token["access_token"])
        return TwitchUser.get_or_create_from_user_obj(user_obj)

    def redirect_path(self):
        if self.state["next"]:
            return self.state["next"]
        else:
            return reverse("index")

    def check_invalid_login(self):
        if self.request.GET.get("error"):
            messages.info(self.request, self.request.GET.get("error_description"))
            return True

        if not self.state:
            messages.info(self.request, "Login expired, try again")
            return True

    @lazy
    def state(self):
        return oauth.State.retrieve(self.request.GET.get("state"))
