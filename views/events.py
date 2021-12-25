from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from classic_tetris_project.facades.qualifier_table import QualifierTable
from classic_tetris_project.models import Event, Qualifier
from classic_tetris_project.util import lazy
from .base import BaseView


class EventView(BaseView):
    @lazy
    def event(self):
        try:
            return Event.objects.get(slug=self.kwargs["event_slug"])
        except Event.DoesNotExist:
            raise Http404()

    @lazy
    def qualifier(self):
        return Qualifier.objects.filter(user=self.current_user, event=self.event).first()

    def ineligible_redirect(self):
        if self.qualifier and self.qualifier.submitted:
            return redirect(reverse("qualifier", args=[self.qualifier.id]))

        messages.info(self.request,
                      "You are no longer able to qualify for this event. If this is in error, "
                      "please contact a moderator.")
        return redirect(reverse("event:index", args=[self.event.slug]))


class IndexView(EventView):
    def get(self, request, event_slug):
        return render(request, "event/index.html", {
            "event": self.event,
            "user_ineligible_reason": self.event.user_ineligible_reason(self.current_user),
            "qualifier_groups": QualifierTable(self.event).groups(),
        })


# Begin qualifier
class QualifyView(LoginRequiredMixin, EventView):
    def get(self, request, event_slug):
        if not self.event.is_user_eligible(self.current_user):
            return self.ineligible_redirect()
        if self.qualifier:
            return redirect(reverse("event:qualifier", args=[self.event.slug]))

        return render(request, "event/qualify.html", {
            "event": self.event,
        })

    def post(self, request, event_slug):
        if not self.event.is_user_eligible(self.current_user):
            return self.ineligible_redirect()
        if self.qualifier:
            return redirect(reverse("event:qualifier", args=[self.event.slug]))

        qualifier = Qualifier.objects.create(user=self.current_user, event=self.event)
        qualifier.report_started()
        return redirect(reverse("event:qualifier", args=[self.event.slug]))


# Submit qualifier
class QualifierView(LoginRequiredMixin, EventView):
    def get(self, request, event_slug):
        if not self.event.is_user_eligible(self.current_user):
            return self.ineligible_redirect()
        if not self.qualifier:
            return redirect(reverse("event:qualify", args=[self.event.slug]))

        return render(request, "event/qualifier.html", {
            "event": self.event,
            "qualifier": self.qualifier,
            "form": self.qualifier.type.form(),
        })

    def post(self, request, event_slug):
        if not self.event.is_user_eligible(self.current_user):
            return self.ineligible_redirect()
        if not self.qualifier:
            return redirect(reverse("event:qualify", args=[self.event.slug]))

        form = self.qualifier.type.form(request.POST)
        if form.is_valid():
            form.save()
            messages.info(self.request, "Qualifier successfully recorded.")
            return redirect(reverse("event:index", args=[self.event.slug]))
        else:
            return render(request, "event/qualifier.html", {
                "event": self.event,
                "qualifier": self.qualifier,
                "form": form,
            })
