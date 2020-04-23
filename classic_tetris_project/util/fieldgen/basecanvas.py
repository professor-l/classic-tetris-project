import io


class BaseCanvas(object):
    def __init__(self, template_image):
        self.img = template_image.copy()
        self.frames = []

    def clone_baseimg(self):
        return self.img.copy()

    def add_frame(self, other_image):
        self.frames.append(other_image)

    def export_bytearray(self):
        byte_array = io.BytesIO()
        if len(self.frames) == 0:
            self.img.save(byte_array, format="png")
        else:
            self.img.save(
                byte_array,
                format="gif",
                save_all=True,
                append_images=self.frames,
                delay=0.060,
                loop=0,
            )
        byte_array.seek(0)
        return byte_array
