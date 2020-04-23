from .tiles import TileMath
from .ai import Aesthetics

class GarbageGenerator(object):
    TETRIS_HEIGHT = 4
    def __init__(self, tile_gen):
        self.tile_gen = tile_gen

    def draw_garbage(self, image, garbage_height, level, target_column):
        # draws garbage tiles on field. Leaves 4 rows in target_column at the top
        block_choices = self.tile_gen.get_block_tiles(level)
        
        # tile coordinate starts.
        x_start = TileMath.FIELD_START[0]
        y_start = TileMath.FIELD_START[1] + (TileMath.FIELD_HEIGHT - garbage_height)
    
        for y in range(garbage_height):
            if y < self.TETRIS_HEIGHT:
                t_c = target_column
            else:                
                t_c = Aesthetics.which_garbage_hole(target_column, y)
            for x in range(TileMath.FIELD_WIDTH):
                if x == t_c:
                    continue
                block = Aesthetics.which_garbage_tile(x, y, block_choices)
                coord = [x_start+x, y_start+y]
                image.paste(block, TileMath.tile_indices_to_pixels(coord))