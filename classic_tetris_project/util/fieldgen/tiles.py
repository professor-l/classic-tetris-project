from PIL import Image
from enum import Enum

class InputTile(Enum):
    LEFT = 0
    DOT = 1
    RIGHT = 2
    LEFT_GRAY = 3
    DOT_GRAY = 4
    RIGHT_GRAY = 5
    COUNT = 6

def TileMath(object):
    # maths support class for positioning tiles and pixels
    # since the position is global to the template, we store 
    # these values here, rather than inside their respective
    # classes.
    BLOCK_SIZE = 8
    FIELD_START = (1,1)
    FIELD_WIDTH = 10
    FIELD_HEIGHT = 20

    INPUT_START = (12,0)
    INPUT_WIDTH = 7
    INPUT_HEIGHT = 7
    # converting from tile-indice to pixel coordinates
    @staticmethod
    def get_block_rect(coord):
        coord_tr = (coord[0]*BLOCK_SIZE, coord[1]*BLOCK_SIZE)
        coord_br = (coord_tr[0]+BLOCK_SIZE-1, coord_tr[1] + BLOCK_SIZE-1)
        return coord_tr + coord_br
    
    # managing locations    
    @staticmethod
    def get_input_coord(self, index):
        # returns the tile-index-coord of a given input index
        x = index % INPUT_WIDTH
        y = index // INPUT_WIDTH
        result = [INPUT_START[0] + x, INPUT_START[1] + y] 
        return result
    
    @staticmethod
    def get_playfield_coord(self, coord):
        # returns the tile-index-coord of a given playfield coordinate
        # coordinates are in x,y format
        return (coord[0]+FIELD_START[0], coord[1]+FIELD_START[1])
    
    @staticmethod
    def tile_index_to_pixel(self, tile):
        return tile * BLOCK_SIZE
    
    @staticmethod
    def tile_indices_to_pixels(self, tile_indices):
        # modifies an tile-coordinate [x, y ..] in-place
        # returns the modified array
        for i, item in enumerate(tile_indices):
            tile_indices[i] = item * BLOCK_SIZE
        return tile_indices


def ImageLoader(object):
    # base class that enables loading of images
    def __init__(self, asset_path):
        self.asset_path = asset_path
                
    # loading / caching our images
    def load_image(self,name):
        file_path = os.path.join(self.asset_path, name)
        return Image.open(file_path)

def TemplateManager(ImageLoader):
    # Since this isn't a tile, it belongs in its own class
    TEMPLATE = "template.png"
    def __init__(self, *args):
        super(TemplateManager, self).__init__(*args)
        self.template = load_image(TEMPLATE)


def TileManager(ImageLoader):
    # class that is in charge of providing image tiles 
    NUMBER_FILE = "numbers.png"
    BLOCK_FILE = "block_tiles.png"
    ARROW_FILE = "arrows.png"

    def __init__(self):
        print('wtf tilemanager')
        #super(TileManager, self).__init__(*args)
        self.numbers = self.load_image(NUMBER_FILE)
        self.block_tiles = self.load_image(BLOCK_FILE)
        self.arrows = ArrowTileManager(self.load_image(ARROW_FILE))
    
    # loading / caching our images
    def load_image(self,name):
        file_path = os.path.join(self.asset_path, name)
        return Image.open(file_path)
    
    def get_block_tiles(self, level):
        # return non-i piece tiles for a given level
        block1 = self.block_tiles.crop(TileMath.get_block_rect([1,level%10]))
        block2 = self.block_tiles.crop(TileMath.get_block_rect([2,level%10]))
        return (block1, block2)
    
    def get_arrow(self, tile_type):
        # returns a copy of an arrow tile
        return self.arrows[tile_type].copy()
        
def ArrowTileManager(object):

    def __init__(self, image):
        self.tiles = split_tiles(image)
    
    def split_tiles(self, image):        
        result = {}
        for i in range(InputTile.COUNT):
            rect = [i,0,i+1,1]
            rect = TileMath.tile_indices_to_pixels(rect)
            result[InputTile(i)] = image.crop(rect)
        return result
    
    def get_tile(self, tile_type):
        return self.tiles[tile_type].copy()


if __name__ == '__main__':
    atm = ArrowTileManager(None)