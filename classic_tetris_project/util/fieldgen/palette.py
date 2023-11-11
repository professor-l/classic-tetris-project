from .tiles import ImageLoader


class Palette(ImageLoader):
    WIDTH = 16
    HEIGHT = 4

    def __init__(self, *args):
        # sets asset_path
        super(Palette, self).__init__(*args)

        self.colors = self.load_colors("palette.png")

    def load_colors(self, image_name):
        image = self.load_image(image_name).convert("RGB")
        pix = image.load()
        result = []

        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                row.append(pix[x, y])
            result.append(row)
        return result

    def get_color(self, hex_offset):
        # F3 = 15 across, 3 down, which is the last digit.
        col = hex_offset // 16
        row = hex_offset % 16
        return self.colors[row][col]

    def find_color_index(self, color):
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                if self.colors[y][x] == color:
                    return 16 * x + y
        raise ValueError("Color not found in data!", color)
