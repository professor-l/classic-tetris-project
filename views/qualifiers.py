from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect, render, reverse
from furl import furl

from classic_tetris_project.models import Qualifier
from classic_tetris_project.util import lazy
from .base import BaseView


class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Qualifier
        fields = ["withdrawn"]
        widgets = {
            "withdrawn": forms.HiddenInput(),
        }


class QualifierView(BaseView):
    def get(self, request, id):
        return render(request, "qualifiers/show.html", {
            "qualifier": self.qualifier,
            "can_withdraw": self.can_withdraw(),
            "withdraw_form": WithdrawForm(initial={"withdrawn": True}),
        })

    # Withdraw qualifier
    def post(self, request, id):
        if not self.can_withdraw():
            raise PermissionDenied
        withdraw_form = WithdrawForm(request.POST, instance=self.qualifier)
        if withdraw_form.is_valid():
            withdraw_form.save()
            if withdraw_form.cleaned_data["withdrawn"]:
                messages.info(self.request, "Your qualifier has been withdrawn.")
        return redirect(reverse("qualifier", args=[self.qualifier.id]))


    @lazy
    def qualifier(self):
        try:
            return Qualifier.objects.get(id=self.kwargs["id"])
        except Qualifier.DoesNotExist:
            raise Http404()

    def can_withdraw(self):
        return (self.qualifier.user == self.current_user and
                self.qualifier.event.qualifying_open and
                self.qualifier.submitted and
                (not self.qualifier.withdrawn))
