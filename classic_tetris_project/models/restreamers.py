from django.db import models

from .users import User


class Restreamer(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="restreamer")
    active = models.BooleanField(default=True)
