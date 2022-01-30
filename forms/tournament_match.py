from dal import autocomplete
from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django_select2 import forms as s2forms

from classic_tetris_project.models import TwitchChannel
from classic_tetris_project.models import Match
from .. import widgets


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["channel", "start_date"]

    channel = forms.ModelChoiceField(
        queryset=TwitchChannel.objects.all(),
        widget=autocomplete.ModelSelect2(url=reverse("autocomplete:twitch_channel")),
    )
    start_date = forms.DateTimeField(widget=widgets.DateTimePicker)


class ReportForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["wins1", "wins2", "channel", "vod", "ended_at"]

    channel = forms.ModelChoiceField(
        queryset=TwitchChannel.objects.all(),
        widget=autocomplete.ModelSelect2(url=reverse("autocomplete:twitch_channel")),
    )
    ended_at = forms.DateTimeField(widget=widgets.DateTimePicker, required=False)

    def clean(self):
        if self.cleaned_data["wins1"] == self.cleaned_data["wins2"]:
            raise ValidationError("One player must have won more games than the other")

    def save(self, reported_by):
        super().save()
        self.instance.end(reported_by)
