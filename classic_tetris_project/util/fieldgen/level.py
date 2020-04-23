from .tiles import TileMath
class LevelGenerator(object):
    def __init__(self, tile_gen):
        self.tile_gen = tile_gen
    
    def draw_level(self, image, level):
        level %= 99
        first = self.tile_gen.get_number_tile(level // 10)
        second = self.tile_gen.get_number_tile(level % 10)
        first_coord = TileMath.tile_indices_to_pixels([15,16])
        second_coord = TileMath.tile_indices_to_pixels([16,16])
        image.paste(first, first_coord)
        image.paste(second, second_coord)