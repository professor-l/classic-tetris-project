from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from classic_tetris_project.facades.qualifier_table import QualifierTable
from classic_tetris_project.models import Event, Qualifier
from classic_tetris_project.util import lazy
from classic_tetris_project import tasks
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
        return Qualifier.objects.filter(user=self.current_user, event=self.event, submitted=False).first()

    def ineligible_redirect(self):
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
            "pending_qualifiers": list(self.event.qualifiers.filter(submitted=True, approved=None)
                                       .order_by("-qualifying_score")),
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
        tasks.announce_qualifier.delay(qualifier.id)
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
            "form": (self.event.form_class)(),
        })

    def post(self, request, event_slug):
        if not self.event.is_user_eligible(self.current_user):
            return self.ineligible_redirect()
        if not self.qualifier:
            return redirect(reverse("event:qualify", args=[self.event.slug]))

        form = (self.event.form_class)(request.POST)
        if form.is_valid():
            form.save(self.qualifier)
            messages.info(self.request, "Qualifier successfully recorded.")
            return redirect(reverse("event:index", args=[self.event.slug]))
        else:
            return render(request, "event/qualifier.html", {
                "event": self.event,
                "qualifier": self.qualifier,
                "form": form,
            })
