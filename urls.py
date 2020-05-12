from django.urls import include, path

from .views import oauth
from .views import simulations
from .views.index import index

oauth_patterns = ([
    path("login/", oauth.login, name="login"),
    path("authorize/", oauth.authorize, name="authorize"),
    path("logout/", oauth.logout, name="logout"),
], "oauth")

simulations_patterns = ([
    path("hz.gif", simulations.HzView.as_view(), name="hz"),
], "simulations")

urlpatterns = [
    path("", index, name="index"),
    path("oauth/", include(oauth_patterns)),
    path("simulations/", include(simulations_patterns)),
]
