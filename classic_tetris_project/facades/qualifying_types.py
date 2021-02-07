from django import forms
from django.utils import timezone


class QualifyingType:
    class Form(forms.Form):
        def __init__(self, qualifying_type, *args, **kwargs):
            submitting = kwargs.pop("submitting", True)
            super().__init__(*args, **kwargs)
            self.qualifying_type = qualifying_type
            # If we're not submitting, ignore vod and details fields
            if not submitting:
                del self.fields["vod"]
                del self.fields["details"]

        vod = forms.URLField(label="VOD")
        details = forms.CharField(widget=forms.Textarea, required=False, label="Details")

        # Fields to display when submitting a qualifier
        def submit_fields(self):
            for field in ([field for field, _ in self.qualifying_type.EXTRA_FIELDS] +
                          ["vod", "details"]):
                yield self[field]

        # Fields to display when editing a qualifier
        def edit_fields(self):
            for field, _ in self.qualifying_type.EXTRA_FIELDS:
                yield self[field]

        def save(self):
            self.qualifying_type.save_form(self.cleaned_data)


    def __init__(self, qualifier):
        self.qualifier = qualifier
        self.vod = qualifier.vod
        self.details = qualifier.details
        self.load_data(self.qualifier.qualifying_data)

    def display_values(self):
        return ([(label, getattr(self, value)) for value, label in self.EXTRA_FIELDS] +
                [("Total score", self.qualifier.qualifying_score)])

    def form(self, *args):
        submitting = not self.qualifier.submitted
        initial = {
            "vod": self.vod,
            "details": self.details,
        }
        for field, _ in self.EXTRA_FIELDS:
            initial[field] = getattr(self, field)

        return self.Form(self, *args, initial=initial, submitting=submitting)

    def save(self):
        self.qualifier.vod = self.vod
        self.qualifier.details = self.details
        self.qualifier.qualifying_score = self.qualifying_score()
        self.qualifier.qualifying_data = self.qualifying_data()
        self.qualifier.save()

    def save_form(self, cleaned_data):
        submit = not self.qualifier.submitted
        if submit:
            self.qualifier.submitted = True
            self.qualifier.submitted_at = timezone.now()

        for attr, value in cleaned_data.items():
            setattr(self, attr, value)

        self.save()

        if submit:
            from classic_tetris_project import tasks
            tasks.report_submitted_qualifier.delay(self.qualifier.id)



class HighestScore(QualifyingType):
    NAME = "Highest Score"
    EXTRA_FIELDS = [
        ("score", "Score"),
    ]

    class Form(QualifyingType.Form):
        score = forms.IntegerField(min_value=0, label="Score")

    def load_data(self, data):
        self.score = data[0] if data else None

    def qualifying_score(self):
        return self.score

    def qualifying_data(self):
        return [self.score]


class Highest2Scores(QualifyingType):
    NAME = "Highest 2 Scores"
    EXTRA_FIELDS = [
        ("score1", "Score 1"),
        ("score2", "Score 2"),
    ]

    class Form(QualifyingType.Form):
        score1 = forms.IntegerField(min_value=0, label="Score 1")
        score2 = forms.IntegerField(min_value=0, label="Score 2")

    def load_data(self, data):
        self.score1 = data[0] if data else None
        self.score2 = data[1] if data else None

    def qualifying_score(self):
        return (self.score1 + self.score2) // 2

    def qualifying_data(self):
        return list(reversed(sorted([self.score1, self.score2])))


class Highest3Scores(QualifyingType):
    NAME = "Highest 3 Scores"
    EXTRA_FIELDS = [
        ("score1", "Score 1"),
        ("score2", "Score 2"),
        ("score3", "Score 3"),
    ]

    class Form(QualifyingType.Form):
        score1 = forms.IntegerField(min_value=0, label="Score 1")
        score2 = forms.IntegerField(min_value=0, label="Score 2")
        score3 = forms.IntegerField(min_value=0, label="Score 3")

    def load_data(self, data):
        self.score1 = data[0] if data else None
        self.score2 = data[1] if data else None
        self.score3 = data[2] if data else None

    def qualifying_score(self):
        return (self.score1 + self.score2 + self.score3) // 3

    def qualifying_data(self):
        return list(reversed(sorted([self.score1, self.score2, self.score3])))


QUALIFYING_TYPES = {
    1: HighestScore,
    2: Highest2Scores,
    3: Highest3Scores,
}
CHOICES = [(n, qualifying_type.NAME) for n, qualifying_type in QUALIFYING_TYPES.items()]
