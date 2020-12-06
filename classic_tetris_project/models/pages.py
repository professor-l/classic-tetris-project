from django.db import models
from django.urls import reverse
from markdownx.models import MarkdownxField

class Page(models.Model):
    title = models.CharField(max_length=64)
    slug = models.SlugField(db_index=True)
    public = models.BooleanField(default=False)
    content = MarkdownxField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("page", args=[self.slug])

    def __str__(self):
        return self.title
