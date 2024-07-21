from enum import Enum

class Platform(Enum):
    DISCORD = 0
    TWITCH = 1
    def display_name(self):
        if self == Platform.DISCORD:
            return "Discord"
        elif self == Platform.TWITCH:
            return "Twitch"
        else:
            raise ValueError("Unhandled platform", self)

class DocSection(Enum):
    USER = 0
    ACCOUNT = 1
    QUEUE = 2
    UTIL = 3
    OTHER = 4
