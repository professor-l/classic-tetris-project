from environ import Env
from django.conf import settings

assert isinstance(settings.ENV, Env)
env = settings.ENV
