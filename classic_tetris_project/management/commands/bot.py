from django.core.management.base import BaseCommand, CommandError
from asgiref.sync import sync_to_async
from celery import current_app as celery_app
from threading import Thread

from ... import discord, twitch
from ...env import env
from ...commands.command_context import DiscordCommandContext, TwitchCommandContext

"""
The discord.py library uses asyncio coroutines for all event 
handlers and blocking API calls. That's nice, but for now we
don't want that to leak into the rest of our application, where
blocking synchronous functions (e.g. Django's ORM operations)
will interfere with the event loop.

Instead, we've decided to write our application synchronously.
This involves dispatching events in a new thread and 
re-entering the event loop when calling async discord.py 
functions.

Some useful background on this approach is discussed in this
article:
https://www.aeracode.org/2018/02/19/python-async-simplified/
"""

class Command(BaseCommand):
    def run_discord(self):
        @discord.client.event
        async def on_ready():
            print("Connected to Discord")

        @discord.client.event
        async def on_message(message):
            if DiscordCommandContext.is_command(message.content):
                context = DiscordCommandContext(message)
                await sync_to_async(context.dispatch)()

        discord.client.run(env("DISCORD_TOKEN"))

    def run_twitch(self):
        @twitch.client.on_welcome
        def on_welcome():
            print("Connected to Twitch")

        @twitch.client.on_message
        def on_message(message):
            if TwitchCommandContext.is_command(message.content):
                context = TwitchCommandContext(message)
                context.dispatch()

        twitch.client.start()

    def handle(self, *args, **options):
        twitch_thread = Thread(target=self.run_twitch)
        twitch_thread.start()
        self.run_discord()
