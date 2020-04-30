from .palette import Palette
from .tiles import ImageLoader, TileMath
from .levelcolor import LevelColor

class BlockTile(ImageLoader):
    TEMPLATE = "block_tile.png"
    GREY = (128,128,128)
    WHITE = (255,255,255)
    def __init__(self, *args):
        super(BlockTile, self).__init__(*args)
        image = self.load_image(self.TEMPLATE).convert("RGB")
        bk_size = TileMath.BLOCK_SIZE
        self.white_tile = image.crop((0,0,bk_size,bk_size))        
        self.color_tile = image.crop((bk_size,0,bk_size*2,bk_size))
        
        palette = Palette(self.asset_path)
        self.levelcolor = LevelColor(palette)
        
    def get_active_tile(self, level):
        white_tile = self.white_tile.copy()
        w, _, c2 = self.levelcolor.get_colors(level)               
        white_tile = self.warp_color(white_tile, w, c2)        
        return white_tile

    def get_field_tiles(self, level):        
        tile1 = self.color_tile.copy()
        tile2 = self.color_tile.copy()
        
        w, c1, c2 = self.levelcolor.get_colors(level)
                
        tile1 = self.warp_color(tile1, w, c1)
        tile2 = self.warp_color(tile2, w, c2)
        return (tile2,tile1)   

    def warp_color(self, tile, white, color):
        pix_data = tile.load()
        for y in range(tile.size[1]):
            for x in range(tile.size[0]):
                if pix_data[x,y] == self.GREY:
                    pix_data[x,y] = color
                elif pix_data[x,y] == self.WHITE:
                    pix_data[x,y] = white
        return tile