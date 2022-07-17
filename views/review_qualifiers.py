from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from classic_tetris_project.facades.user_permissions import UserPermissions
from classic_tetris_project.models import Qualifier
from classic_tetris_project.util import lazy
from ..forms.review_qualifiers import ReviewQualifierForm
from .base import BaseView


class ReviewQualifiersView(PermissionRequiredMixin, BaseView):
    permission_required = UserPermissions.REVIEW_QUALIFIERS


class IndexView(ReviewQualifiersView):
    def get(self, request):
        return render(request, "review_qualifiers/index.html", {
            "qualifiers": list(Qualifier.objects.pending_review().order_by("created_at")),
        })


class ReviewView(ReviewQualifiersView):
    def get(self, request, qualifier_id):
        if self.qualifier.approved is not None:
            messages.info(self.request, "That qualifier has already been reviewed.")
            return redirect(reverse("review_qualifiers:index"))

        return render(request, "review_qualifiers/review.haml", {
            "qualifier": self.qualifier,
            "edit_form": self.qualifier.type.form(),
            "review_form": ReviewQualifierForm(),
        })

    def post(self, request, qualifier_id):
        if self.qualifier.approved is not None:
            messages.info(self.request, "That qualifier has already been reviewed.")
            return redirect(reverse("review_qualifiers:index"))

        edit_form = self.qualifier.type.form(request.POST)
        review_form = ReviewQualifierForm(request.POST)
        if edit_form.is_valid() and review_form.is_valid():
            edit_form.save()
            review_form.save(self.qualifier, self.current_user)
            if self.qualifier.approved:
                messages.info(self.request, "Qualifier approved")
            elif self.qualifier.approved:
                messages.info(self.request, "Qualifier rejected")
            return redirect(reverse("review_qualifiers:index"))
        else:
            return render(request, "review_qualifiers/review.haml", {
                "qualifier": self.qualifier,
                "edit_form": edit_form,
                "review_form": review_form,
            })

    @lazy
    def qualifier(self):
        try:
            return Qualifier.objects.filter(submitted=True).get(id=self.kwargs["qualifier_id"])
        except Qualifier.DoesNotExist:
            raise Http404()
