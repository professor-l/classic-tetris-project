from django import template
from django.utils.safestring import mark_safe
import markdown as md

from classic_tetris_project.models import Page

register = template.Library()

@register.filter
def markdown(value):
    return mark_safe(md.markdown(value))


@register.simple_tag
def page(slug):
    try:
        page = Page.objects.get(slug=slug)
        return mark_safe(md.markdown(page.content))
    except Page.DoesNotExist:
        return ""
