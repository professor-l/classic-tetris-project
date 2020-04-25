class GravityFrames(object):
    LEVELS = [
        48,
        43,
        38,
        33,
        28,
        23,
        18,
        13,
        8,
        6,
        5,
        5,
        5,
        4,
        4,
        4,
        3,
        3,
        3,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
    ]

    @staticmethod
    def get_gravityframes(level):
        result = 1
        level %= 256
        if level < 29:
            result = GravityFrames.LEVELS[level]
        return result
