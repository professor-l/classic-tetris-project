from django import forms
from django.utils.safestring import mark_safe

from classic_tetris_project.models import Qualifier


class ReviewQualifierFormMeta(forms.forms.DeclarativeFieldsMetaclass):
        def __new__(mcs, name, bases, attrs):
            for check, label in Qualifier.REVIEWER_CHECKS:
                field = forms.BooleanField(label=label, label_suffix="?", initial=True, required=False)
                attrs[check] = field
            return super().__new__(mcs, name, bases, attrs)


class ReviewQualifierForm(forms.Form, metaclass=ReviewQualifierFormMeta):
    notes = forms.CharField(widget=forms.Textarea, required=False)
    approved = forms.TypedChoiceField(coerce=lambda x: x == "True",
                                      choices=((True, "Approve"), (False, "Reject")),
                                      widget=forms.RadioSelect)

    def checks(self):
        for check, _ in Qualifier.REVIEWER_CHECKS:
            yield self[check]

    def save(self, qualifier, reviewed_by):
        qualifier.review(
            self.cleaned_data["approved"],
            reviewed_by,
            checks={ key: self.cleaned_data[key] for key, _ in Qualifier.REVIEWER_CHECKS },
            notes=self.cleaned_data["notes"]
        )
