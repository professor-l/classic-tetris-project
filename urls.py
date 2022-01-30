from django.urls import include, path

from .views import autocomplete
from .views import oauth
from .views import simulations
from .views.index import index
from .views import user
from .views import profile
from .views import policy
from .views import pages
from .views import events
from .views import qualifiers
from .views import review_qualifiers
from .views import tournaments
from .views import tournament_matches


autocomplete_patterns = ([
    path("twitch-channel/", autocomplete.TwitchChannelAutocomplete.as_view(),
         name="twitch_channel"),
], "autocomplete")

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

tournament_match_patterns = ([
    path("", tournament_matches.IndexView.as_view(), name="index"),
    path("schedule/", tournament_matches.ScheduleView.as_view(), name="schedule"),
    path("report/", tournament_matches.ReportView.as_view(), name="report"),
], "match")

tournament_patterns = ([
    path("", tournaments.IndexView.as_view(), name="index"),
    path("match/<int:match_number>/", include(tournament_match_patterns)),
], "tournament")

event_patterns = ([
    path("", events.IndexView.as_view(), name="index"),
    path("qualify/", events.QualifyView.as_view(), name="qualify"),
    path("qualifier/", events.QualifierView.as_view(), name="qualifier"),
    path("<slug:tournament_slug>/", include(tournament_patterns)),
], "event")

review_qualifiers_patterns = ([
    path("", review_qualifiers.IndexView.as_view(), name="index"),
    path("<int:qualifier_id>/", review_qualifiers.ReviewView.as_view(), name="review"),
], "review_qualifiers")


urlpatterns = [
    path("", index, name="index"),
    path("ac/", include(autocomplete_patterns)),
    path("oauth/", include(oauth_patterns)),
    path("simulations/", include(simulations_patterns)),
    path("user/<str:id>/", user.UserView.as_view(), name="user"),
    path("profile/", include(profile_patterns)),
    path("policy/", include(policy_patterns)),
    path("page/<slug:page_slug>/", pages.page, name="page"),
    path("event/<slug:event_slug>/", include(event_patterns)),
    path("qualifier/<int:id>/", qualifiers.QualifierView.as_view(), name="qualifier"),
    path("review_qualifiers/", include(review_qualifiers_patterns)),

    path("markdownx/", include('markdownx.urls')),
]
