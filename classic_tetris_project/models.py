from django.db import models

class User(models.Model):
    preferred_name = models.CharField(max_length=64, null=True)
    ntsc_pb = models.IntegerField(null=True)
    pal_pb = models.IntegerField(null=True)