class LevelGenerator(object):
    def __init__(self, tile_gen):
        self.tile_gen = tile_gen
    
    def draw_level(self, canvas, level):
        if level <= 99:        
            first = NUMBERS.crop(get_block_rect([level//10,0]))
            second = NUMBERS.crop(get_block_rect([level%10,0]))
            canvas.paste(first,get_block_rect([15,16]))
            canvas.paste(second,get_block_rect([16,16]))