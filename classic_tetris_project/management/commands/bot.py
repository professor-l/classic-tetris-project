from asgiref.sync import sync_to_async
import asyncio
import time
from threading import Thread
import logging.config
import yaml

from django.core.management.base import BaseCommand, CommandError

from ... import discord, twitch
from ...commands.command_context import DiscordCommandContext, TwitchCommandContext, ReportCommandContext, ScheduleCommandContext
from ...moderation.moderator import DiscordModerator
from ...env import env
from ...logging import LoggingManager
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

        @discord.client.event
        async def on_message_edit(before, after):
            if DiscordModerator.is_rule(after):
                moderator = DiscordModerator(after)
                await sync_to_async(moderator.dispatch)()

        @discord.client.event
        async def on_message(message):
            if DiscordModerator.is_rule(message):
                moderator = DiscordModerator(message)
                await sync_to_async(moderator.dispatch)()
                
            if DiscordCommandContext.is_command(message.content):
                context = DiscordCommandContext(message)
                await sync_to_async(context.dispatch)()
                
            if ReportCommandContext.is_command(message.content):
                context = ReportCommandContext(message)
                await sync_to_async(context.dispatch)()

            if ScheduleCommandContext.is_command(message.content):
                context = ScheduleCommandContext(message)
                await sync_to_async(context.dispatch)()

        discord.client.run(env("DISCORD_TOKEN"))

    def run_twitch(self):
        @twitch.client.on_welcome
        def on_welcome():
            twitch.logger.info("Connected to twitch")

        @twitch.client.on_message
        def on_message(message):
            if TwitchCommandContext.is_command(message.content):
                context = TwitchCommandContext(message)
                context.dispatch()

        @twitch.client.on_reconnect
        def on_reconnect():
            guild = discord.get_guild()
            # tries to fetch guild for 5 seconds, and returns if it fails
            timeout = 5
            while guild is None:
                if timeout == 0:
                    return
                timeout -= 1
                time.sleep(1)
                guild = discord.get_guild()
            chan = guild.get_channel(discord.MAINTENANCE_CHAN_ID)
            # not using async_to_sync because this function needs to be run in
            # the discord event loop
            # source: https://stackoverflow.com/questions/52232177/runtimeerror-timeout-context-manager-should-be-used-inside-a-task
            asyncio.run_coroutine_threadsafe(chan.send("Twitch bot was disconnected, attempting to reconnect..."), discord.client.loop)

        twitch.client.start()

    def handle(self, *args, **options):
        LoggingManager.setup()
        twitch_thread = Thread(target=self.run_twitch)
        twitch_thread.start()
        self.run_discord()
