from images.rect import Rect
from .base import Operation


class CropOperation(Operation):

    def construct(self):
        pass

    def run(self, willow, image, env):
        focal_point = image.get_focal_point()
        if focal_point:
            willow = willow.crop(focal_point)
        return willow
