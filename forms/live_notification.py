from django import forms

POSITIONS =[
    ('topleft', 'Top Left'),
    ('topright', 'Top Right'),
    ('bottomleft', 'Bottom Left'),
    ('bottomright', 'Bottom Right'),
    ('centerleft', 'Center Left'),
    ('centerright', 'Center Right'),
    ('center', 'Center'),
]

class LiveNotificationForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, required=False)
    duration = forms.IntegerField(label="Duration", min_value=0, max_value=100, required=False)
    position = forms.ChoiceField(choices=POSITIONS, widget=forms.RadioSelect, initial="topleft")
