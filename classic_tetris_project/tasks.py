import re
from celery import shared_task
from disco.types.message import MessageEmbed
from django.template.loader import render_to_string

from . import discord_disco as discord
from .models import Qualifier
from .env import env


QUALIFIER_COLOR_APPROVED = 0x07D12F
QUALIFIER_COLOR_REJECTED = 0xE60000


@shared_task
def report_reviewed_qualifier(qualifier_id):
    qualifier = Qualifier.objects.get(id=qualifier_id)
    event = qualifier.event
    discord_user = qualifier.user.discord_user

    # Send message to user
    user_embed = MessageEmbed()
    user_embed.description = render_to_string("discord/qualifier_reviewed_user.txt", {
        "event_name": event.name,
        "event_url": event.get_absolute_url(True),
        "qualifier": qualifier,
        "checks": ([(description, qualifier.review_data["checks"][check])
                    for check, description in Qualifier.REVIEWER_CHECKS
                    if check in qualifier.review_data["checks"]]
                   if qualifier.review_data["checks"] else None),
    }).replace("\\\n", "").strip()
    user_embed.color = (QUALIFIER_COLOR_APPROVED if qualifier.approved else QUALIFIER_COLOR_REJECTED)

    discord.send_direct_message(discord_user.discord_id, embed=user_embed)

    # Send message to channel
    channel_id = env("DISCORD_QUALIFIER_REPORTING_CHANNEL_ID")
    if qualifier.approved and channel_id:
        channel_embed = MessageEmbed()
        channel_embed.description = render_to_string("discord/qualifier_reviewed_channel.txt", {
            "event_name": event.name,
            "event_url": event.get_absolute_url(True),
            "qualifier": qualifier,
        }).replace("\\\n", "").strip()
        channel_embed.color = QUALIFIER_COLOR_APPROVED
        discord.send_channel_message(channel_id, embed=channel_embed)
