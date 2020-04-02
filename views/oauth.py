from django.contrib import auth, messages
from django.shortcuts import redirect
from django.urls import reverse

from ...models import DiscordUser, WebsiteUser
from ..oauth import discord as discord_oauth


def login(request):
    redirect_uri = request.build_absolute_uri(reverse("oauth:authorize"))
    return discord_oauth.authorize_redirect(request, redirect_uri)


def authorize(request):
    if request.GET.get("error"):
        messages.info(request, request.GET.get("error_description"))
        return redirect(reverse("index"))

    token = discord_oauth.authorize_access_token(request)
    response = discord_oauth.get("users/@me", token=token)
    user = response.json()

    discord_user = DiscordUser.fetch_by_discord_id(user["id"])
    discord_user.username = user["username"]
    discord_user.save()

    website_user = WebsiteUser.fetch_by_user(discord_user.user)
    auth.login(request, website_user.auth_user)
    return redirect(reverse("index"))


def logout(request):
    auth.logout(request)
    return redirect(reverse("index"))
