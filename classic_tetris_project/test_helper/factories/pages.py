import factory

from classic_tetris_project.models import *


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page
