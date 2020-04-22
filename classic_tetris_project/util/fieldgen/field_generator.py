import os.path
import random
from PIL import Image
from PIL import features
import io

LEVELS = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
ANIMATIONS_ALLOWED = features.check("webp_anim")
if not ANIMATIONS_ALLOWED:
    print ("Please enable WebP support by running 'pip-install webp'")
    print ("Then reinstalling pillow with 'pip uninstall Pillow'")
    print ("and finally 'pip install Pillow'")

def get_file_root():
    return os.path.dirname(os.path.abspath(__file__))

def load_image(name):
    file_path = os.path.join(get_file_root(), name)
    return Image.open(file_path)

def load_arrows():
    base_img = load_image("arrows.png")
    order = ['LEFT','DOT','RIGHT','LEFT_G','DOT_G','RIGHT_G']
    result = {}
    for i, item in enumerate(order):
        rect = [i*BLOCK_SIZE,0,(i+1)*BLOCK_SIZE,BLOCK_SIZE]
        result[item] = base_img.crop(rect)
    return result

BLOCK_SIZE = 8
FIELD_START = (1,1)
WIDTH = 10
HEIGHT = 20
  
NUMBERS     = load_image("numbers.png")
BLOCK_TILES = load_image("block_tiles.png")
TEMPLATE    = load_image("template.png")
ARROWS = load_arrows()

def save_image(img, frames):
    byte_array = io.BytesIO()
    if len(frames) == 0:
        img.save(byte_array,format='png')
    else:
        img.save(byte_array,
                format='gif',
                save_all=True,
                append_images=frames,
                delay=0.016,
                loop=0)
    byte_array.seek(0)
    return byte_array

def get_arrow(sequence, gray=False):
    target_column = get_target_column(sequence)
    g = "_G" if gray else ""
    return ARROWS["LEFT"+g] if target_column < 5 else ARROWS["RIGHT"+g]

def get_target_column(sequence):
    left_right = -1 if len(sequence) % 2 == 1 else 1
    return 5 + len(sequence) * left_right

#returns a BLOCK_SIZE block as a LTRB rectangle
def get_block_rect(coord):
    coord_tr = (coord[0]*BLOCK_SIZE, coord[1]*BLOCK_SIZE)
    coord_br = (coord_tr[0]+BLOCK_SIZE-1, coord_tr[1] + BLOCK_SIZE-1)
    return coord_tr + coord_br

MAX_SEQ = 7*7

def get_input_coord(index):
    start = [12,0]
    width = 7
    x = index % width
    y = index // width
    start[0] += x
    start[1] += y
    return [start[0] * BLOCK_SIZE, start[1] * BLOCK_SIZE]


def generate_field(level, height, sequence):
    canvas = TEMPLATE.copy()
    generate_first(canvas,level,height,sequence)
    seq_length = sequence[-1]+1
    if not ANIMATIONS_ALLOWED or seq_length > MAX_SEQ:
        return save_image(canvas,[])

    frames = []
    gravity = 1
    if (level % 256) < 29:
        gravity = LEVELS[level]

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
        new_frame = canvas.copy()
        
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

        frames.append(new_frame)
    
    return save_image(canvas, frames)
    
def generate_first(canvas, level, height, sequence):
    block1 = BLOCK_TILES.crop(get_block_rect([1,level%10]))
    block2 = BLOCK_TILES.crop(get_block_rect([2,level%10]))
    
    x_start = FIELD_START[0] * BLOCK_SIZE
    y_start = (FIELD_START[1] + (HEIGHT-height)) * BLOCK_SIZE
    
    target_column = get_target_column(sequence)
    for y in range(height):
        if y < 4:
            t_c = target_column
        else:
            cells = [i for i in range(10)]
            cells.remove(target_column)
            t_c = random.choice(cells)
        for x in range(WIDTH):
            if x == t_c:
                continue
            block = block1 if random.random() < 0.5 else block2
            coord = [x_start+x*BLOCK_SIZE,y_start+y*BLOCK_SIZE]
            canvas.paste(block, coord)
    
    # input
    arrow = get_arrow(sequence, True)
    len_seq = sequence[-1]+1
    if len_seq <= MAX_SEQ:
        for i in range(len_seq):
            coord = get_input_coord(i)
            if i in sequence:
                canvas.paste(arrow,coord)
            else:
                canvas.paste(ARROWS["DOT_G"],coord)
    # level
    if level <= 99:        
        first = NUMBERS.crop(get_block_rect([level//10,0]))
        second = NUMBERS.crop(get_block_rect([level%10,0]))
        canvas.paste(first,get_block_rect([15,16]))
        canvas.paste(second,get_block_rect([16,16]))

if __name__ == '__main__':
    generate_field(19,7,[0,6,10,49])