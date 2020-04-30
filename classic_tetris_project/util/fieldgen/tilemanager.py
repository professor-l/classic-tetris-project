from enum import IntEnum
from PIL import Image
from .tiles import ImageLoader, TileMath
from .blocktile import BlockTile
import os

class InputTile(IntEnum):
    LEFT = 0
    DOT = 1
    RIGHT = 2
    LEFT_GRAY = 3
    DOT_GRAY = 4
    RIGHT_GRAY = 5
    COUNT = 6

class TileManager(ImageLoader):
    # class that is in charge of providing image tiles
    NUMBER_FILE = "numbers.png"    
    ARROW_FILE = "arrows.png"

    def __init__(self, *args):
        super(TileManager, self).__init__(*args)
        self.numbers = self.load_image(self.NUMBER_FILE)
        self.block_tiles = BlockTile(self.asset_path)
        self.arrows = ArrowTileManager(self.load_image(self.ARROW_FILE))

    def get_active_piece_tile(self, level):
        return self.block_tiles.get_active_tile(level)

    def get_block_tiles(self, level):
        return self.block_tiles.get_field_tiles(level)

    def get_number_tile(self, number):
        return self.numbers.crop(TileMath.get_block_rect([number, 0]))

    def get_arrow(self, tile_type):
        return self.arrows.get_tile(tile_type)

class ArrowTileManager(object):
    def __init__(self, image):
        self.tiles = self.split_tiles(image)

    def split_tiles(self, image):
        result = {}
        for i in range(int(InputTile.COUNT)):
            rect = [i, 0, i + 1, 1]
            rect = TileMath.tile_indices_to_pixels(rect)
            result[InputTile(i)] = image.crop(rect)
        return result

    def get_tile(self, tile_type):
        # returns a copy of an arrow tile
        return self.tiles[tile_type].copy()
