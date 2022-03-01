from django.db import models, transaction
from django.db.models import signals
from django.utils import timezone
from django.utils.html import format_html

from .. import tasks
from .users import User
from .events import Event
from ..facades import qualifying_types
from ..words import Words
from ..util import lazy


class QualifierQuerySet(models.QuerySet):
    def pending_review(self):
        return self.filter(submitted=True, approved=None, withdrawn=False)

    def active(self):
        return self.filter(submitted=True, approved=True, withdrawn=False)

    def public(self):
        return self.filter(submitted=True, withdrawn=False).exclude(approved=False)

class Qualifier(models.Model):
    REVIEWER_CHECKS = [
        ("stencil", "Stencil ready"),
        ("rom", "Unmodified ROM"),
        ("timer", "Timer on screen"),
        ("reset", "Hard reset before starting"),
        ("auth_word", "Entered correct auth word"),
        ("auth_word_score", "Auth word score over 10k"),
        ("correct_scores", "Submitted correct score(s)"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, related_name="qualifiers", on_delete=models.CASCADE)
    auth_word = models.CharField(max_length=6)
    qualifying_type = models.IntegerField(choices=qualifying_types.CHOICES)
    qualifying_score = models.IntegerField(blank=True, null=True)
    qualifying_data = models.JSONField(blank=True, null=True)
    vod = models.URLField(null=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)

    approved = models.BooleanField(default=None, null=True)
    review_data = models.JSONField(default=dict)
    reviewed_at = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(User, related_name="qualifiers_reviewed",
                                    on_delete=models.SET_NULL, null=True)
    withdrawn = models.BooleanField(default=False)


    objects = QualifierQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "user"],
                                    name="unique_event_user"),
        ]


    def review(self, approved, reviewed_by, checks, notes):
        self.approved = approved
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.review_data = {
            "checks": checks,
            "notes": notes,
        }
        self.save()
        self.report_reviewed()

    @lazy
    def type(self):
        return qualifying_types.QUALIFYING_TYPES[self.qualifying_type](self)

    @lazy
    def tournament(self):
        if hasattr(self, "tournament_player"):
            return self.tournament_player.tournament

    def status_tag(self):
        # Move this somewhere better in the future
        def render_tag(text, style):
            return format_html(
                "<span class='status-tag status-tag--{}'>{}</span>",
                style,
                text
            )

        if self.withdrawn:
            return render_tag("Withdrawn", "gray")
        elif not self.submitted:
            return render_tag("Not Submitted", "gray")
        elif self.approved == True:
            return render_tag("Approved", "green")
        elif self.approved == False:
            return render_tag("Rejected", "red")
        else:
            return render_tag("Pending Review", "gray")

    @staticmethod
    def before_save(sender, instance, **kwargs):
        if not instance.auth_word:
            instance.auth_word = Words.get_word()
        if not instance.qualifying_type:
            instance.qualifying_type = instance.event.qualifying_type

    def report_started(self):
        transaction.on_commit(lambda: tasks.announce_qualifier.delay(self.id))

    def report_submitted(self):
        transaction.on_commit(lambda: tasks.report_submitted_qualifier.delay(self.id))

    def report_reviewed(self):
        transaction.on_commit(lambda: tasks.report_reviewed_qualifier.delay(self.id))

    def __str__(self):
        return f"{self.user.display_name} ({self.event.name})"

signals.pre_save.connect(Qualifier.before_save, sender=Qualifier)
