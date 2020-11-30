from django import forms

from classic_tetris_project.models import Qualifier

class ThreeScoreAverageForm(forms.Form):
    score1 = forms.IntegerField(min_value=0)
    score2 = forms.IntegerField(min_value=0)
    score3 = forms.IntegerField(min_value=0)
    vod = forms.URLField()
    details = forms.CharField(widget=forms.Textarea, required=False)

    def save(self, event, user):
        qualifying_score = (self.cleaned_data["score1"] + self.cleaned_data["score2"] +
                            self.cleaned_data["score3"]) // 3
        qualifying_data = [self.cleaned_data["score1"], self.cleaned_data["score2"],
                           self.cleaned_data["score3"]]
        return Qualifier.objects.create(
            user=user,
            event=event,
            qualifying_score=qualifying_score,
            qualifying_data=qualifying_data,
            vod=self.cleaned_data["vod"],
            details=self.cleaned_data["details"],
        )
