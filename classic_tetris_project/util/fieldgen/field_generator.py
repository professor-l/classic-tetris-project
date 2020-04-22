import os.path
import random
from PIL import Image


def get_file_root():
    return os.path.dirname(os.path.abspath(__file__))

def load_image(name):
    file_path = os.path.join(get_file_root(), name)
    return Image.open(file_path)

NUMBERS     = load_image("numbers.png")
BLOCK_TILES = load_image("block_tiles.png")
TEMPLATE    = load_image("template.png")
BLOCK_SIZE = 8
FIELD_START = (1,1)
WIDTH = 10
HEIGHT = 20

def get_target_column(sequence):
    left_right = -1 if len(sequence) % 2 == 1 else 1
    return 5 + len(sequence) * left_right

#returns a BLOCK_SIZE block as a LTRB rectangle
def get_block_rect(coord):
    coord_tr = (coord[0]*BLOCK_SIZE, coord[1]*BLOCK_SIZE)
    coord_br = (coord_tr[0]+BLOCK_SIZE-1, coord_tr[1] + BLOCK_SIZE-1)
    return coord_tr + coord_br

def generate_field(level, height, sequence):
    canvas = TEMPLATE.copy()
    generate_first(canvas,level,height,sequence)

def generate_first(canvas, level, height, sequence):
    block1 = BLOCK_TILES.crop(get_block_rect([1,level%10]))
    block2 = BLOCK_TILES.crop(get_block_rect([2,level%10]))
    
    x_start = FIELD_START[0] * BLOCK_SIZE
    y_start = (FIELD_START[1] + (HEIGHT-height)) * BLOCK_SIZE
    
    target_column = get_target_column(sequence)
    for x in range(WIDTH):
        if x == target_column:
            continue
        for y in range(height):
            block = block1 if random.random() < 0.5 else block2
            coord = [x_start+x*BLOCK_SIZE,y_start+y*BLOCK_SIZE]
            canvas.paste(block, coord)
    canvas.show()
if __name__ == '__main__':
    generate_field(10,6,[1,2,3,4,5])