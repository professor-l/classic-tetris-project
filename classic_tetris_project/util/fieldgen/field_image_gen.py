from .basecanvas import BaseCanvas
from .tiles import TileManager, TemplateManager
from .assetpath import AssetPath
from .garbage import GarbageGenerator
from .gravity import GravityFrames
from .level import LevelGenerator
from .input import InputGenerator
from .ai import Aesthetics
from .activepiece import ActivePieceGenerator


class FieldImageGenerator(object):
    TILE_MANAGER = TileManager(AssetPath.get_asset_root())
    TEMPLATE_MANAGER = TemplateManager(AssetPath.get_asset_root())

    @staticmethod
    def image(simulation):
        generator = FieldImageGenerator(simulation)
        return generator.generate_image()

    def __init__(self, simulation):
        self.level = simulation.level % 256
        self.height = simulation.height
        self.sequence = simulation.sequence

    def generate_image(self):
        bc = BaseCanvas(self.TEMPLATE_MANAGER.template)
        self.generate_base(bc)

        if InputGenerator.input_too_long(self.sequence):
            return bc.export_bytearray()

        self.simulate_game(bc)
        return bc.export_bytearray()

    def generate_base(self, canvas):
        gg = GarbageGenerator(self.TILE_MANAGER)
        gg.draw_garbage(
            canvas.img,
            self.height,
            self.level,
            Aesthetics.get_target_column(self.sequence),
        )

        ig = InputGenerator(self.TILE_MANAGER)
        ig.draw_input_gray(canvas.img, self.sequence)

        lg = LevelGenerator(self.TILE_MANAGER)
        lg.draw_level(canvas.img, self.level)

    def simulate_game(self, canvas):
        gravity_frames = GravityFrames.get_gravityframes(self.level)
        column_dir = Aesthetics.get_piece_shift_direction(self.sequence)
        seq_length = InputGenerator.input_length(self.sequence)
        anim_length = seq_length + 3 * gravity_frames
        stop_grav = None
        if self.height < GarbageGenerator.TETRIS_HEIGHT:
            stop_grav = anim_length - (4 - self.height) * gravity_frames

        ig = InputGenerator(self.TILE_MANAGER)
        ap = ActivePieceGenerator(self.TILE_MANAGER)

        shifts = 0
        g_counter = 0
        for i in range(anim_length):
            new_frame = canvas.clone_baseimg()

            # input display
            ig.draw_input_red(new_frame, i, self.sequence)

            # perform the simulation
            if i in self.sequence:
                shifts += 1

            if stop_grav is None or g_counter < stop_grav:
                g_counter += 1

            # calculate long bar position
            piece_x = 5 + shifts * column_dir
            piece_y = 0 + g_counter // gravity_frames

            ap.draw_longbar(new_frame, (piece_x, piece_y), self.level)

            canvas.add_frame(new_frame)


if __name__ == "__main__":
    # fg = FieldGenerator()
    bc = TileManager("hello")
    print(bc)
    # fg.generate_image(19,7,[0,6,10,49])
