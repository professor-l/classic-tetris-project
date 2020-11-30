from django.urls import include, path

from .views import oauth
from .views import simulations
from .views.index import index
from .views import user
from .views import profile
from .views import policy
from .views import pages
from .views import events

oauth_patterns = ([
    path("login/", oauth.login, name="login"),
    path("login/<str:provider>/", oauth.LoginView.as_view(), name="login"),
    path("authorize/<str:provider>/", oauth.AuthorizeView.as_view(), name="authorize"),
    path("logout/", oauth.logout, name="logout"),
], "oauth")

simulations_patterns = ([
    path("hz.gif", simulations.HzView.as_view(), name="hz"),
], "simulations")

profile_patterns = ([
    path("", profile.ProfileView.as_view()),
    path("edit/", profile.ProfileEditView.as_view(), name="edit"),
], "profile")

policy_patterns = ([
    path("cookies/", policy.cookies, name="cookies"),
], "policy")

event_patterns = ([
    path("", events.IndexView.as_view(), name="index"),
    path("qualify/", events.QualifyView.as_view(), name="qualify"),
], "event")


urlpatterns = [
    path("", index, name="index"),
    path("oauth/", include(oauth_patterns)),
    path("simulations/", include(simulations_patterns)),
    path("user/<str:id>/", user.UserView.as_view(), name="user"),
    path("profile/", include(profile_patterns)),
    path("policy/", include(policy_patterns)),
    path("page/<slug:page_slug>/", pages.page, name="page"),
    path("event/<slug:event_slug>/", include(event_patterns)),

    path("markdownx/", include('markdownx.urls')),
]
