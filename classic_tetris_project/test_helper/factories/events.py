import factory
from django.utils.text import slugify

from classic_tetris_project.models import *
from classic_tetris_project.test_helper.factories.users import *


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event
    name = factory.Sequence(lambda n: f"Event {n}")
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    qualifying_type = 1

class QualifierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Qualifier
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)

    class Params:
        submitted_ = factory.Trait(
            qualifying_score=500000,
            qualifying_data=[500000],
            vod="https://twitch.tv/asdf",
            submitted=True,
        )

        approved_ = factory.Trait(
            submitted_=True,
            approved=True
        )
