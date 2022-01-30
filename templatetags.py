from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
import markdown as md

from classic_tetris_project.models import Page


register = template.Library()

@register.simple_tag
def markdown(value):
    return render_to_string("templatetags/markdown.html", {
        "content": mark_safe(md.markdown(value, extensions=settings.MARKDOWNX_MARKDOWN_EXTENSIONS)),
    })


@register.simple_tag
def page(slug):
    try:
        page = Page.objects.get(slug=slug)
        return markdown(page.content)
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

@register.tag
def field_list_row(parser, token):
    nodelist = parser.parse(("endfield_list_row",))
    parser.delete_first_token()
    return FieldListRowNode(nodelist, *token.split_contents()[1:])

class FieldListRowNode(template.Node):
    def __init__(self, nodelist, label, value=None):
        self.nodelist = nodelist
        self.label = template.Variable(label)
        self.value = template.Variable(value) if value else None

    def render(self, context):
        return render_to_string("templatetags/field_list_row.haml", {
            "label": self.label.resolve(context),
            "value": self.value.resolve(context) if self.value else self.nodelist.render(context),
        })

@register.tag
def field_list_input_row(parser, token):
    nodelist = parser.parse(("endfield_list_input_row",))
    parser.delete_first_token()
    return FieldListInputRowNode(nodelist, *token.split_contents()[1:])

class FieldListInputRowNode(template.Node):
    def __init__(self, nodelist, label, field=None):
        self.nodelist = nodelist
        self.label = template.Variable(label)
        self.field = template.Variable(field) if field else None

    def render(self, context):
        return render_to_string("templatetags/field_list_input_row.haml", {
            "label": self.label.resolve(context),
            "field": self.field.resolve(context) if self.field else None,
            "content": self.nodelist.render(context),
        })


# TODO automate this on registration
import hamlpy.template.loaders
hamlpy.template.loaders.options["custom_self_closing_tags"] = {
    "module": "endmodule",
    "field_list_row": "endfield_list_row",
    "field_list_input_row": "endfield_list_input_row",
}
