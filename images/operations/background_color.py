from .base import Operation
from images.utils import parse_color_string


class BackgroundColorOperation(Operation):
    def construct(self, color_string):
        self.color = parse_color_string(color_string)

    def run(self, willow, image, env):
        return willow.set_background_color_rgb(self.color)
