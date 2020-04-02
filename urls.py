from django.urls import include, path

from .views import oauth
from .views.index import index

oauth_patterns = ([
    path("login/", oauth.login, name="login"),
    path("authorize/", oauth.authorize, name="authorize"),
], "oauth")

urlpatterns = [
    path("", index, name="index"),
    path("oauth/", include(oauth_patterns)),
]
