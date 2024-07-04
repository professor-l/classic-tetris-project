from django import forms
from classic_tetris_project.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["preferred_name", "pronouns", "country", "playstyle"]
