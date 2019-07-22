from celery import shared_task
from asgiref.sync import async_to_sync

from .discord import discord_client
from .models.users import DiscordUser

@shared_task
def send_message_to_discord_user(discord_user_id, message):
    discord_user = DiscordUser.objects.get(id=discord_user_id)
    discord_user_obj = discord_client.get_user(int(discord_user.discord_id))
    async_to_sync(discord_user_obj.send)(message)
