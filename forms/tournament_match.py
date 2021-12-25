from dal import autocomplete
from django import forms
from django.urls import reverse
from django_select2 import forms as s2forms

from classic_tetris_project.models import TwitchChannel
from classic_tetris_project.models import Match
from .. import widgets


class RestreamForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["channel", "start_date"]

    channel = forms.ModelChoiceField(
        queryset=TwitchChannel.objects.all(),
        widget=autocomplete.ModelSelect2(url=reverse("autocomplete:twitch_channel")),
    )
    start_date = forms.DateTimeField(widget=widgets.DateTimePicker(attrs={"autocomplete":"off"}))

    def save(self, tournament_match):
        self.instance = tournament_match.get_or_create_match()
        super().save()
