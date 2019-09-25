from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand, CommandError
from threading import Thread
import logging.config
import yaml

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
            discord.logger.info("Connected to Discord")
            # print("Connected to Discord")

        @discord.client.event
        async def on_message(message):
            if DiscordCommandContext.is_command(message.content):
                context = DiscordCommandContext(message)
                await sync_to_async(context.dispatch)()

        discord.client.run(env("DISCORD_TOKEN"))

    def run_twitch(self):
        @twitch.client.on_welcome
        def on_welcome():
            twitch.logger.info("Connected to twitch")
            # print("Connected to twitch")

        @twitch.client.on_message
        def on_message(message):
            if TwitchCommandContext.is_command(message.content):
                context = TwitchCommandContext(message)
                context.dispatch()

        twitch.client.start()

    def handle(self, *args, **options):

        import sys
        import logging.handlers

        import os
        try:
            os.mkdir("logs")
        except FileExistsError:
            pass

        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)


        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename="logs/bot.log",
            when="midnight",
            interval=1
        )

        from datetime import datetime
        def namer(name):
            return datetime.now().strftime("logs/bot-%Y-%m-%d.log")

        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.namer = namer

        discord.logger.addHandler(console_handler)
        discord.logger.addHandler(file_handler)
        discord.logger.setLevel(logging.DEBUG)
        twitch.logger.addHandler(console_handler)
        twitch.logger.addHandler(file_handler)
        twitch.logger.setLevel(logging.DEBUG)


        twitch_thread = Thread(target=self.run_twitch)
        twitch_thread.start()
        self.run_discord()
        # """
