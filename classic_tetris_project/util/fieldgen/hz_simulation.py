import math
from .gravity import GravityFrames
from .field_image_gen import FieldImageGenerator


class HzSimulation(object):
    def __init__(self, level, height, taps=None, sequence=None):

        self.level = int(level)
        self.height = int(height)
        if taps is not None:
            self.taps = int(taps)
            self.frames = self.generate_numframes()

        if sequence is not None:
            self.sequence = sequence
            self.taps = len(self.sequence)
            self.frames = sequence[-1] + 1
        elif taps is not None:
            self.sequence = self.generate_sequence(taps)
        else:
            raise RuntimeError("taps or sequence must be provided")

    def generate_numframes(self):
        gravity = GravityFrames.get_gravityframes(self.level)
        return gravity * (19 - self.height)

    def generate_sequence(self, num_taps):
        if (
            self.level < 0
            or self.height < 0
            or self.height > 19
            or self.taps < 1
            or self.taps > 5
        ):
            raise ValueError("`Unrealistic parameters.`")

        if self.taps == 1:
            raise ValueError(
                "`You have {fr} frames to time this tap (and maybe a rotation for polevault).`".format(
                    fr=self.frames
                )
            )

        if 2 * self.taps - 1 > self.frames:
            raise ValueError("`Not even TAS can do this.`")

        return self.input_seq(self.frames, self.taps)

    def input_seq(self, frames, taps):
        mini = frames / (taps - 1) - 0.1
        indices = []
        for i in range(0, taps):
            indices.append(math.floor(mini * i))

        return indices

    def hertz(self):
        mini = round(60 * (self.taps - 1) / self.frames, 2)
        maxi = round(60 * self.taps / self.frames, 2)

        return (mini, maxi)

    def image(self):
        if self.is_cached():
            return self.cached_image()
        else:
            return FieldImageGenerator.image(self)

    def printable_sequence(self):
        result = list("." * self.frames)
        for item in self.sequence:
            result[item] = "X"
        return "".join(result)

    def is_cached(self):
        return False  # stub

    def cached_image(self):
        return None  # stub
