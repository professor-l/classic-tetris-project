from enum import Enum
class Platform(Enum):
    DISCORD = 0
    TWITCH = 1

def comma_separate(score):
    return f"{score:,}"
