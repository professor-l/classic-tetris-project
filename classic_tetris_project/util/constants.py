from enum import Enum

class Platform(Enum):
    DISCORD = 0
    TWITCH = 1

class DocSection(Enum):
    USER = 0
    ACCOUNT = 1
    QUEUE = 2
    UTIL = 3
    OTHER = 4
