from .base import Operation


class WidthHeightOperation(Operation):
    def construct(self, size):
        self.size = int(size)

    def run(self, willow, image, env):
        image_width, image_height = willow.get_size()

        if self.method == 'width':
            if image_width <= self.size:
                return

            scale = self.size / image_width

            width = self.size
            height = int(image_height * scale)

        elif self.method == 'height':
            if image_height <= self.size:
                return

            scale = self.size / image_height

            width = int(image_width * scale)
            height = self.size

        else:
            # Unknown method
            return

        return willow.resize((width, height))
