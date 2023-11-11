from .tiles import TileMath
from .tilemanager import InputTile
from .ai import Aesthetics


class InputGenerator(object):
    MAX_SEQ = TileMath.INPUT_HEIGHT * TileMath.INPUT_WIDTH

    def __init__(self, tile_gen):
        self.tile_gen = tile_gen

    @staticmethod
    def input_length(sequence):
        return sequence[-1] + 1

    @staticmethod
    def input_too_long(sequence):
        return InputGenerator.input_length(sequence) > InputGenerator.MAX_SEQ

    @staticmethod
    def max_sequence_length():
        return InputGenerator.MAX_SEQ

    def draw_input_gray(self, image, sequence):
        arrow_tile = self.get_direction_arrow(sequence, True)
        dot_tile = self.tile_gen.get_arrow(InputTile.DOT_GRAY)
        len_seq = sequence[-1] + 1
        if len_seq <= self.MAX_SEQ:
            for i in range(len_seq):
                tile = arrow_tile if i in sequence else dot_tile
                self.paste_tile_on_index(image, i, tile)

    def draw_input_red(self, image, index, sequence):
        # unfortunately we have to pass the entire sequence,
        # since we don't want to leak direction of the arrow
        # to the outside space
        if index in sequence:
            tile = self.get_direction_arrow(sequence, False)
        else:
            tile = self.tile_gen.get_arrow(InputTile.DOT)

        if index <= sequence[-1]:
            self.paste_tile_on_index(image, index, tile)

    def paste_tile_on_index(self, image, index, tile):
        # pastes an image tile in the right spot, given its index
        coord = TileMath.get_input_coord(index)
        coord = TileMath.tile_indices_to_pixels(coord)
        image.paste(tile, coord)

    def get_direction_arrow(self, sequence, gray=False):
        # returns a red/gray left/right arrow correctly based on AI
        direction = Aesthetics.get_piece_shift_direction(sequence)
        if direction < 0:
            target = InputTile.LEFT_GRAY if gray else InputTile.LEFT
            arrow = self.tile_gen.get_arrow(target)
        else:
            target = InputTile.RIGHT_GRAY if gray else InputTile.RIGHT
            arrow = self.tile_gen.get_arrow(target)
        return arrow
