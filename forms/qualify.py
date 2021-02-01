from django import forms

from classic_tetris_project.models import Qualifier


class QualifyingForm(forms.Form):
    vod = forms.URLField()
    details = forms.CharField(widget=forms.Textarea, required=False)

    def save(self, qualifier):
        qualifier.submitted = True
        qualifier.vod = self.cleaned_data["vod"]
        qualifier.details = self.cleaned_data["details"]
        for attr, value in self.score_data().items():
            setattr(qualifier, attr, value)
        qualifier.save()

    def score_data(self):
        {}


class HighestScoreForm(QualifyingForm):
    score = forms.IntegerField(min_value=0)

    def score_data(self):
        return {
            "qualifying_score": self.cleaned_data["score"],
            "qualifying_data": [self.cleaned_data["score"]],
        }

    def qualify_template(self):
        return "event/qualify_forms/highest_score.html"


class Highest3ScoresForm(QualifyingForm):
    score1 = forms.IntegerField(min_value=0)
    score2 = forms.IntegerField(min_value=0)
    score3 = forms.IntegerField(min_value=0)

    def score_data(self):
        qualifying_score = (self.cleaned_data["score1"] + self.cleaned_data["score2"] +
                            self.cleaned_data["score3"]) // 3
        qualifying_data = [self.cleaned_data["score1"], self.cleaned_data["score2"],
                           self.cleaned_data["score3"]]
        return {
            "qualifying_score": qualifying_score,
            "qualifying_data": qualifying_data,
        }

    def qualify_template(self):
        return "event/qualify_forms/highest_3_scores.html"
