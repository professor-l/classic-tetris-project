from django.urls import path

from .views.index import index
from .views.accounts.login import LoginView

urlpatterns = [
    path("", index, name="index"),

    path("accounts/login/", LoginView.as_view()),
]
