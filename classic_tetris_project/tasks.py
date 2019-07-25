from celery import shared_task

from .discord import discord_client
from .models.users import DiscordUser



@shared_task
def discord_send_message_to_user(discord_user_id, message):
    discord_user = DiscordUser.objects.get(id=discord_user_id)
    discord_user_obj = discord_client.get_user(int(discord_user.discord_id))

    discord_client.loop.create_task(discord_user_obj.send(message))
