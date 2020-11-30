from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
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

@register.tag
def module(parser, token):
    nodelist = parser.parse(("endmodule",))
    parser.delete_first_token()
    return ModuleNode(nodelist, *token.split_contents()[1:])

class ModuleNode(template.Node):
    def __init__(self, nodelist, title, header_style=None):
        self.nodelist = nodelist
        self.title = template.Variable(title)
        self.header_style = template.Variable(header_style) if header_style else None

    def render(self, context):
        return render_to_string("templatetags/module.html", {
            "title": self.title.resolve(context),
            "header_style": self.header_style.resolve(context) if self.header_style else None,
            "content": self.nodelist.render(context),
        })
