from datetime import datetime
import logging
import logging.handlers
import os
import sys

from . import discord, twitch


class LoggingManager:
    def __init__(self):
        self.formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)

        self.file_handler = logging.handlers.TimedRotatingFileHandler(
            filename="logs/bot.log",
            when="midnight",
            interval=1
        )
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(self.formatter)
        self.file_handler.namer = lambda name: datetime.now().strftime("logs/bot-%Y-%m-%d.log")

    def bind(self, logger):
        logger.addHandler(self.console_handler)
        logger.addHandler(self.file_handler)
        logger.setLevel(logging.INFO)

    @staticmethod
    def setup():
        try:
            os.mkdir("logs")
        except FileExistsError:
            pass

        manager = LoggingManager()
        manager.bind(discord.logger)
        manager.bind(twitch.logger)
