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
            "qualifiers": list(Qualifier.objects.filter(approved=None).order_by("created_at")),
        })


class ReviewView(ReviewQualifiersView):
    def get(self, request, qualifier_id):
        if self.qualifier.approved is not None:
            messages.info(self.request, "That qualifier has already been reviewed.")
            return redirect(reverse("review_qualifiers:index"))

        return render(request, "review_qualifiers/review.html", {
            "qualifier": self.qualifier,
            "form": ReviewQualifierForm(),
        })

    def post(self, request, qualifier_id):
        if self.qualifier.approved is not None:
            messages.info(self.request, "That qualifier has already been reviewed.")
            return redirect(reverse("review_qualifiers:index"))

        form = ReviewQualifierForm(request.POST)
        if form.is_valid():
            form.save(self.qualifier, self.current_user)
            if self.qualifier.approved:
                messages.info(self.request, "Qualifier approved")
            elif self.qualifier.approved:
                messages.info(self.request, "Qualifier rejected")
            return redirect(reverse("review_qualifiers:index"))
        else:
            return render(request, "review_qualifiers/review.html", {
                "qualifier": self.qualifier,
                "form": form,
            })

    @lazy
    def qualifier(self):
        try:
            return Qualifier.objects.get(id=self.kwargs["qualifier_id"])
        except Qualifier.DoesNotExist:
            raise Http404()
