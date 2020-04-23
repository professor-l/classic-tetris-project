from .tiles import TileMath, InputTile
from .ai import Aesthetics

class InputGenerator(object):


    def __init__(self, tile_gen):
        self.tile_gen = tile_gen
    
    @staticmethod
    def input_length(sequence):
        return sequence[-1] + 1
    
    @staticmethod
    def input_too_long(sequence):
        return input_length(sequence) > max_sequence_length()

    @staticmethod 
    def max_sequence_length():
        return TileMath.INPUT_HEIGHT * TileMath.INPUT_WIDTH

    def draw_input_gray(self, canvas, sequence):
        arrow_tile = self.get_direction_arrow(sequence, True)
        dot_tile = self.tilegen.get_arrow(InputTile.DOT_GRAY)
        len_seq = sequence[-1]+1
        if len_seq <= MAX_SEQ:
            for i in range(len_seq):
                tile = arrow_tile if i in sequence else dot_tile
                self.paste_tile_on_index(canvas, i, tile)
    
    def draw_input_red(self, canvas, index, sequence):
        # unfortunately we have to pass the entire sequence,
        # since we don't want to leak direction of the arrow
        # to the outside space
        if index in sequence:
            tile = self.get_direction_arrow(sequence, False)
        else: 
            tile = self.tilegen.get_arrow(InputTile.DOT)

        self.paste_tile_on_index(canvas, index, tile)
   
    def paste_tile_on_index(self, canvas, index, tile):
        # pastes an image tile in the right spot, given its index
        coord = TileMath.get_input_coord(i)
        coord = TileMath.tile_indices_to_pixels(coord)
        if i in sequence:
            canvas.paste(arrow_tile,coord)
        else:
            canvas.paste(dot_tile,coord)

    def get_direction_arrow(self, sequence, gray=False):
        # returns a red/gray left/right arrow correctly based on AI
        direction = Aesthetics.get_piece_shift_direction(sequence)
        if direction < 0:
            target = InputTile.LEFT_GRAY if gray else InputTile.LEFT
            arrow = tile_gen.get_arrow(target)
        else:
            target = InputTile.RIGHT_GRAY if gray else InputTile.RIGHT
            arrow = tile_gen.get_arrow(target)
        return result