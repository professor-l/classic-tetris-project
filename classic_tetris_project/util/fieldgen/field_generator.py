import os.path
import random
from PIL import Image
from .basecanvas import BaseCanvas
from .tiles import TileManager, TileMath, TemplateManager
from .assetpath import AssetPath
from .garbage import GarbageGenerator
from .gravity import GravityFrames
from .level import LevelGenerator
from .input import InputGenerator
from .ai import Aesthetics

class FieldGenerator(object):
    TILE_MANAGER = TileManager(AssetPath.get_asset_root())
    TEMPLATE_MANAGER = TemplateManager(AssetPath.get_asset_root())
    def __init__(self, level, height, sequence):
        self.level = level
        self.height = height
        self.sequence = sequence

    def generate_image(self):
        bc = BaseCanvas(self.TEMPLATE_MANAGER.template)
        self.generate_base(bc)

        if InputGenerator.input_too_long(self.sequence):
            return bc.export_bytearray()
        
        #self.simulate_game(bc, level, height, sequence)
        return bc.export_bytearray()

    def generate_base(self, canvas):
        gg = GarbageGenerator(self.TILE_MANAGER)
        gg.draw_garbage(canvas.img, self.height, self.level, 
                        Aesthetics.get_target_column(self.sequence))

        ig = InputGenerator(self.TILE_MANAGER)
        ig.draw_input_gray(canvas.img, self.sequence)
    
        lg = LevelGenerator(self.TILE_MANAGER)
        lg.draw_level(canvas.img, self.level)
    
    def simulate_game(self, canvas):
        gravity_frames = GravityFrames.get_gravityframes(self.level)

        shifts = 0
        g_counter = 0            
        column_dir = Aesthetics.get_piece_shift_direction(self.sequence)
        
        seq_length = InputGenerator.input_length(self.sequence)
        anim_length = seq_length + 3 * gravity
        stop_grav = None
        if height < GarbageGenerator.TETRIS_HEIGHT:
            stop_grav = anim_length - (4 - height)*gravity
        
        ig = InputGenerator(self.TILE_MANAGER)
        #ap = ActivePieceGenerator(self.TILE_MANAGER)

        for i in range(anim_length):
            new_frame = bc.clone_baseimg()
        
            # input display
            ig.draw_input_red(new_frame, i, sequence)
            
            if i in sequence:            
                shifts += 1
            
            if stop_grav is None or g_counter < stop_grav:
                g_counter += 1
            
            row_offset = 2 + g_counter // gravity
            
            # I piece paster
            piece_x = 6 + shifts * column_dir
            for j in range(4):
                row = row_offset - j
                if row >= 1:
                    new_frame.paste(block,(get_block_rect([piece_x,row])))

            bc.add_frame(new_frame)
    

def simulate_game(bc, level,height,sequence):
    

    
    return save_image(canvas, frames)

if __name__ == '__main__':
    #fg = FieldGenerator()
    bc = TileManager("hello")
    print(bc)
    #fg.generate_image(19,7,[0,6,10,49])
    