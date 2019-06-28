from django.contrib import admin

from .models.users import User

admin.site.register(User)