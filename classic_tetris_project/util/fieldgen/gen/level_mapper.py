import PIL
import os.path
import PIL.ImageDraw  
import sys


# following is a hack to import Palette, which is in the directory above.
# from https://meatfighter.com/nintendotetrisai/#Coloring_Tetriminos
from ..palette import Palette
from ..tiles import ImageLoader
    
class LevelMapper(ImageLoader):
    START_COORD = (31, 26)
    GROUP_WIDTH = 56
    TILE_Y_OFFSET = 24
    TILE_WIDTH = 17
    
    ROWS = 26
    COLS = 10
    LAST = 256

    COLORS_PER_LEVEL = 3

    # construct with LevelMapper(LevelMapper.get_file_root())
    def __init__(self, *args):
        super(LevelMapper, self).__init__(*args)
        self.palette = Palette(self.asset_path)
    
    @staticmethod
    def get_file_root():
        return os.path.dirname(os.path.abspath(__file__))
    
    def find_level_palettes(self):
        ref_image = self.load_image("levelcolors.png").convert("RGB")
        results = []
        number = 0
        for y in range(self.ROWS):
            row_pos = self.START_COORD[1] + self.TILE_Y_OFFSET * y
            for group_num in range(self.COLS):
                group_x_pos = self.START_COORD[0] + self.GROUP_WIDTH * group_num
                level_palette = self.find_level_palette(ref_image, row_pos, group_x_pos)
                results.append(level_palette)
                number += 1
                if number >= self.LAST:
                    break

        return results

    def find_level_palette(self, image, startY, startX):
        result = []
        for color_idx in range(self.COLORS_PER_LEVEL):
            position = (startX + color_idx * self.TILE_WIDTH, startY)
            color = image.getpixel(position)
            idx = self.palette.find_color_index(color)
            result.append("0x"+ "{:02x}".format(idx))
        return result
    
    @staticmethod
    def pretty_print_palette(level_palette):
        return "[" + ", ".join(level_palette) + "]"
    
    @staticmethod
    def pretty_print(level_palettes):
        result = "[\n"
        lines = []
        for row in range(LevelMapper.ROWS):
            first_index = row*LevelMapper.COLS
            last_index = min((row+1)*LevelMapper.COLS, LevelMapper.LAST)
            chunk = level_palettes[first_index:last_index]
            line = ", ".join(LevelMapper.pretty_print_palette(p) for p in chunk)
            lines.append(line)
        return "[\n" + ",\n".join(lines) + "\n]"

# run this by using
# cd classic_tetris_project/util
# python -m fieldgen.gen.level_mapper 

if __name__ == '__main__':
    lm = LevelMapper(LevelMapper.get_file_root())
    result = lm.find_level_palettes()
    print(LevelMapper.pretty_print(result))
    