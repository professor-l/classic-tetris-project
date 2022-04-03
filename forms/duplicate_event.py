from django import forms
from django.db import transaction

from classic_tetris_project.models import Event


class DuplicateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name"]

    @transaction.atomic
    def save(self, base_event):
        event = Event.objects.create(
            name=self.cleaned_data["name"],
            qualifying_type=base_event.qualifying_type,
            pre_qualifying_instructions=base_event.pre_qualifying_instructions,
            qualifying_instructions=base_event.qualifying_instructions,
            event_info=base_event.event_info,
        )
        for tournament in base_event.tournaments.all():
            event.tournaments.create(
                short_name=tournament.short_name,
                order=tournament.order,
                seed_count=tournament.seed_count,
                placeholders=tournament.placeholders,
                color=tournament.color,
                restreamed=tournament.restreamed,
                details=tournament.details,
                discord_emote_string=tournament.discord_emote_string
            )
        return event
