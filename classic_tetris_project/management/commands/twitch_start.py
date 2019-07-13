from django.core.management.base import BaseCommand

from ... import twitch
from ...env import env
from ...commands.command_context import TwitchCommandContext


class Command(BaseCommand):
    def handle(self, *args, **options):
        # import logging
        # logging.basicConfig(level=logging.DEBUG)
        client = twitch.Client(
            env("TWITCH_USERNAME"),
            env("TWITCH_TOKEN"),
            channels=["classictetrisbottest"]
        )

        @client.on_message
        def on_message(message):
            if TwitchCommandContext.is_command(message.content):
                context = TwitchCommandContext(message)
                context.dispatch()

        client.start()
