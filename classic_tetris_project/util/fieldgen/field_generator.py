import os.path
import random
from PIL import Image
from .basecanvas import BaseCanvas
from .tiles import TileManager, TileMath, TemplateManager
from .assetpath import AssetPath
from .garbage import GarbageGenerator
from .input import InputGenerator
from .ai import Aesthetics

class FieldGenerator(object):
    TILE_MANAGER = TileManager(AssetPath.get_asset_root())
    TEMPLATE_MANAGER = TemplateManager(AssetPath.get_asset_root())
    def __init__(self):
        self.tester = TileManager(AssetPath.get_asset_root())
        print(self.tester)
    def generate_image(self, level, height, sequence):
        bc = BaseCanvas(self.TEMPLATE_MANAGER.template)
        self.generate_base(bc)

        if InputGenerator.input_too_long(sequence):
            return bc.export_bytearray()
        
        #self.simulate_game(bc, level, height, sequence)
        return bc.export_bytearray()

    def generate_base(self, canvas, level, height, sequence):
        gg = GarbageGenerator(self.TILE_MANAGER)
        gg.draw_garbage(canvas.img, height, level, get_target_column(sequence))

        ig = InputGenerator(self.TILE_MANAGER)
        ig.draw_input_gray(canvas.img, sequence)
    
        lg = LevelGenerator(self.TILE_MANAGER)
        lg.draw_level(canvas.img, level)

    def simulate_game(self, canvas, level, height, sequence):
        pass


def simulate_game(bc, level,height,sequence):
    
    gravity_frames = gravity.get_gravity(level)

    shifts = 0
    g_counter = 0
    
    target_column = get_target_column(sequence)
    column_dir = -1 if target_column <= 5 else 1

    arrow = get_arrow(sequence)
    dot = ARROWS["DOT"]
    block = BLOCK_TILES.crop(get_block_rect([0,level%10]))
    seq_length = sequence[-1]+1
    anim_length = seq_length+3*gravity
    stop_grav = None
    if height < 4:
        stop_grav = anim_length - (4 - height)*gravity
    
    for i in range(anim_length):
        new_frame = bc.clone_baseimg()
        
        # input display
        coord = get_input_coord(i)
        if i in sequence:
            new_frame.paste(arrow, coord)
            shifts += 1
        elif i < sequence[-1]+1:
            new_frame.paste(dot, coord)
        if stop_grav is None or g_counter < stop_grav:
            g_counter += 1
        row_offset = 2 + g_counter // gravity
        
        piece_x = 6 + shifts * column_dir
        for j in range(4):
            row = row_offset - j
            if row >= 1:
                new_frame.paste(block,(get_block_rect([piece_x,row])))

        bc.add_frame(new_frame)
    
    return save_image(canvas, frames)

if __name__ == '__main__':
    #fg = FieldGenerator()
    bc = TileManager("hello")
    print(bc)
    #fg.generate_image(19,7,[0,6,10,49])
    