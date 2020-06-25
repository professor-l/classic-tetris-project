from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import UpdateView

from classic_tetris_project.models import User
from .base import BaseView
from ..forms.profile import ProfileForm

class ProfileView(LoginRequiredMixin, BaseView):
    def get(self, request):
        return redirect(self.current_user)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "profile/edit.html"

    def get_object(self):
        return self.request.user.website_user.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
