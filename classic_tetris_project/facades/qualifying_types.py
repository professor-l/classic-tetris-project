from django import forms
from django.db.models.expressions import RawSQL
from django.utils import timezone


class QualifyingType:
    ORDER_BY = ["-qualifying_score"]

    class Form(forms.Form):
        def __init__(self, qualifying_type, *args, **kwargs):
            submitting = kwargs.pop("submitting", True)
            super().__init__(*args, **kwargs)
            self.qualifying_type = qualifying_type

            if not self.qualifying_type.qualifier.event.vod_required:
                self.fields["vod"].help_text = "(optional)"
                self.fields["vod"].required = False

            # If we're not submitting, ignore vod and details fields
            if not submitting:
                del self.fields["vod"]
                del self.fields["details"]

        vod = forms.URLField(label="VOD")
        details = forms.CharField(widget=forms.Textarea, required=False, label="Details",
                                  help_text="(optional)")

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
        return ([(label, self.format_value(field, getattr(self, field))) for field, label in self.EXTRA_FIELDS] +
                [("Total score", self.format_score())])

    def format_value(self, field, value):
        return value

    def format_score(self):
        return "{:,}".format(self.qualifier.qualifying_score)

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
            self.qualifier.report_submitted()



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


class MostMaxouts(QualifyingType):
    NAME = "Most Maxouts"
    EXTRA_FIELDS = [
        ("maxouts", "Maxout Count"),
        ("kicker", "Kicker"),
    ]
    ORDER_BY = [
        RawSQL("(qualifying_data::json->>'maxouts')::integer", ()).desc(),
        RawSQL("(qualifying_data::json->>'kicker')::integer", ()).desc()
    ]

    class Form(QualifyingType.Form):
        maxouts = forms.IntegerField(
            min_value=0, label="Maxout Count",
            help_text=("Total number of maxouts (scores over 999,999) you got. If you did not "
                       "maxout, enter 0.")
        )
        kicker = forms.IntegerField(
            min_value=0, label="Kicker",
            help_text=("Your highest non-maxout score. If you did not maxout, this is your highest "
                       "score.")
        )

    def load_data(self, data):
        self.maxouts = data["maxouts"] if data else None
        self.kicker = data["kicker"] if data else None

    def qualifying_score(self):
        return self.maxouts

    def format_score(self):
        return "{}; {:,}".format(self.maxouts, self.kicker)

    def qualifying_data(self):
        return {
            "maxouts": self.maxouts,
            "kicker": self.kicker,
        }


def format_time(time):
    minutes = int(time // 60)
    seconds = time % 60
    return "{}:{:06.3f}".format(minutes, seconds)

class LowestTime(QualifyingType):
    NAME = "Lowest Time"
    EXTRA_FIELDS = [
        ("time", "Time"),
    ]
    ORDER_BY = ["qualifying_score"] # increasing; lowest time comes first

    class Form(QualifyingType.Form):
        time = forms.DurationField(label="Time", help_text="(e.g. 12:34.567)")

        def __init__(self, *args, **kwargs):
            if kwargs["initial"]["time"]:
                kwargs["initial"]["time"] = format_time(kwargs["initial"]["time"])
            super().__init__(*args, **kwargs)

        def clean_time(self):
            time = self.cleaned_data["time"]
            return time.total_seconds()

    def load_data(self, data):
        self.time = data[0] if data else None

    def qualifying_score(self):
        return round(self.time * 1000)

    def format_value(self, field, value):
        if field == "time":
            return format_time(value)
        else:
            return value

    def format_score(self):
        return format_time(self.time)

    def qualifying_data(self):
        return [self.time]

class Clipped7GameAvg(QualifyingType):
    NAME = "Clipped Seven Game Average"
    EXTRA_FIELDS = [(f"score{i}", f"Score {i}") for i in range(1, 8)]

    class Form(QualifyingType.Form):
        score1 = forms.IntegerField(min_value=0, label="Score 1")
        score2 = forms.IntegerField(min_value=0, label="Score 2")
        score3 = forms.IntegerField(min_value=0, label="Score 3")
        score4 = forms.IntegerField(min_value=0, label="Score 4")
        score5 = forms.IntegerField(min_value=0, label="Score 5")
        score6 = forms.IntegerField(min_value=0, label="Score 6")
        score7 = forms.IntegerField(min_value=0, label="Score 7")

    def load_data(self, data):
        pass
        self.score1 = data[0] if data else None
        self.score2 = data[1] if data else None
        self.score3 = data[2] if data else None
        self.score4 = data[3] if data else None
        self.score5 = data[4] if data else None
        self.score6 = data[5] if data else None
        self.score7 = data[6] if data else None

    def qualifying_score(self):
        scores = list(reversed(sorted([self.score1, self.score2, self.score3, self.score4, self.score5, self.score6, self.score7])))
        scores = scores[1:-1]
        return sum(scores) // 5

    def qualifying_data(self):
        return list(reversed(sorted([self.score1, self.score2, self.score3, self.score4, self.score5, self.score6, self.score7])))

QUALIFYING_TYPES = {
    1: HighestScore,
    2: Highest2Scores,
    3: Highest3Scores,
    4: MostMaxouts,
    5: LowestTime,
    6: Clipped7GameAvg,
}
CHOICES = [(n, qualifying_type.NAME) for n, qualifying_type in QUALIFYING_TYPES.items()]
