from django.http import Http404
from django.shortcuts import render

from classic_tetris_project.models import Page

def page(request, page_slug):
    try:
        page = Page.objects.filter(public=True).get(slug=page_slug)
        return render(request, "pages/page.html", {
            "page": page,
        })
    except Page.DoesNotExist:
        raise Http404()
