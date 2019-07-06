from django.core.management.base import BaseCommand, CommandError
import discord
from ...env import env
from ...commands.command_context import DiscordCommandContext

class Command(BaseCommand):
    def handle(self, *args, **options):
        client = discord.Client()

        @client.event
        async def on_message(message):
            if DiscordCommandContext.is_command(message.content):
                context = DiscordCommandContext(message)
                await context.dispatch()

        client.run(env("DISCORD_TOKEN"))

