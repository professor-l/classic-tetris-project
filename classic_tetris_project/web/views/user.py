from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from classic_tetris_project.models import User, TwitchUser
from classic_tetris_project.util.memo import lazy
from .base import BaseView


class UserView(BaseView):
    def get(self, request, id):
        user = self.get_user(id)
        if hasattr(user, "twitch_user") and id != user.twitch_user.username:
            return redirect(reverse("user", args=[user.twitch_user.username]))

        return render(request, "user/show.haml", {
            "user": user,
            "discord_user": (user.discord_user if hasattr(user, "discord_user") else None),
            "twitch_user": (user.twitch_user if hasattr(user, "twitch_user") else None),
            "pb": f"{user.get_pb():,}",
        })

    def get_user(self, id):
        twitch_user = TwitchUser.from_username(id)
        if twitch_user is not None:
            return twitch_user.user

        try:
            return User.objects.get(id=int(id))
        except (ValueError, User.DoesNotExist):
            raise Http404("User does not exist")
