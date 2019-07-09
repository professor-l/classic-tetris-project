from django.contrib import admin

from .models.users import User, DiscordUser

admin.site.register(User)
admin.site.register(DiscordUser)
