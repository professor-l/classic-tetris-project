import random
from .tiles import TileMath

class Aesthetics(object):
    # Artificially intelligent aesthetics class    
    @staticmethod
    def is_odd(number):
        # artificial intelligence for determining pseudo-random results
        return number % 2 == 1
    
    @staticmethod
    def get_target_column(sequence):
        # returns an artificially intelligently derived column to target, based on a given sequence
        CENTER_COLUMN = TileMath.FIELD_WIDTH // 2        
        left_right = Aesthetics.get_piece_shift_direction(sequence)
        return CENTER_COLUMN + len(sequence) * left_right
    
    @staticmethod        
    def get_piece_shift_direction(sequence):
        # returns -1 or 1 depending on offset from centre column
        left_right = -1 if Aesthetics.is_odd(len(sequence)) else 1
        return left_right

    @staticmethod
    def which_garbage_hole(excluded_column, row):
        # given a target column, decides a column for garbage based on 
        # artificial intelligence and digital aesthetics
        # to do: extend using neural networks.
        cells = [i for i in range(TileMath.FIELD_WIDTH)]
        cells.remove(excluded_column)
        return random.choice(cells)

    @staticmethod
    def which_garbage_tile(target_column, target_row, choices):
        # given a target board position, decides which tile to use,
        # using artificial intelligence and digital aesthetics
        # TODO: extend using machine learning.
        return random.choice(choices)