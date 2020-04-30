from PIL import Image
import os


class TileMath(object):
    # maths support class for positioning tiles and pixels
    # since the position is global to the template, we store
    # these values here, rather than inside their respective
    # classes.
    BLOCK_SIZE = 8
    FIELD_START = (1, 1)  # should we upgrade this to a class?
    FIELD_WIDTH = 10
    FIELD_HEIGHT = 20

    INPUT_START = (12, 0)
    INPUT_WIDTH = 7
    INPUT_HEIGHT = 7

    LEVEL_START = (15, 16)
    LEVEL_END = (16, 16)
    # converting from tile-indice to pixel coordinates
    @staticmethod
    def get_block_rect(coord):
        coord_tr = (coord[0] * TileMath.BLOCK_SIZE, coord[1] * TileMath.BLOCK_SIZE)
        coord_br = (
            coord_tr[0] + TileMath.BLOCK_SIZE - 1,
            coord_tr[1] + TileMath.BLOCK_SIZE - 1,
        )
        return coord_tr + coord_br

    # managing locations
    @staticmethod
    def get_input_coord(index):
        # returns the tile-index-coord of a given input index
        x = index % TileMath.INPUT_WIDTH
        y = index // TileMath.INPUT_WIDTH
        # upgrade to Point or Coord class? then addition will be natural
        # or: tuple(map(lambda x, y: x + y, coord, TileMath.FIELD_START))
        result = [TileMath.INPUT_START[0] + x, TileMath.INPUT_START[1] + y]
        return result

    @staticmethod
    def get_playfield_coord(coord):
        # returns the tile-index-coord of a given playfield coordinate
        # coordinates are in x,y format

        # upgrade to Point or Coord class? then addition will be natural
        # or: tuple(map(lambda x, y: x + y, coord, TileMath.FIELD_START))
        return (coord[0] + TileMath.FIELD_START[0], coord[1] + TileMath.FIELD_START[1])

    @staticmethod
    def tile_index_to_pixel(tile):
        return tile * TileMath.BLOCK_SIZE

    @staticmethod
    def tile_indices_to_pixels(tile_indices):
        # converts from tile coordinates to pixel coordinates
        # returns the modified array
        return [TileMath.tile_index_to_pixel(item) for item in tile_indices]


class ImageLoader(object):
    # base class that enables loading of images
    def __init__(self, asset_path):
        self.asset_path = asset_path

    # loading / caching our images
    def load_image(self, name):
        file_path = os.path.join(self.asset_path, name)
        return Image.open(file_path)


class TemplateManager(ImageLoader):
    # Since this isn't a tile, it belongs in its own class
    TEMPLATE = "template.png"

    def __init__(self, *args):
        super(TemplateManager, self).__init__(*args)
        self.template = self.load_image(self.TEMPLATE)
