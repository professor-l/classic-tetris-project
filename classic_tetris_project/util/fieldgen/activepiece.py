from .tiles import TileMath


class ActivePieceGenerator(object):
    TETROMINO_OFFSETS = [[0, 1], [0, 0], [0, -1], [0, -2]]
    # TETROMINO_OFFSETS = [[0,0],[-1,-1],[0,-1],[1,-1]]
    def __init__(self, tile_gen):
        self.tile_gen = tile_gen

    def draw_longbar(self, image, coords, level):
        tile = self.tile_gen.get_active_piece_tile(level)
        for offset in self.TETROMINO_OFFSETS:
            row = coords[1] + offset[1]
            if row >= 0:
                tile_pos = [coords[0] + offset[0], coords[1] + offset[1]]
                tile_pos = [
                    tile_pos[0] + TileMath.FIELD_START[0],
                    tile_pos[1] + TileMath.FIELD_START[1],
                ]
                image.paste(tile, TileMath.tile_indices_to_pixels(tile_pos))
