from .base import Operation


class JPEGQualityOperation(Operation):
    def construct(self, quality):
        self.quality = int(quality)

        if self.quality > 100:
            raise ValueError("JPEG quality must not be higher than 100")

    def run(self, willow, image, env):
        env['jpeg-quality'] = self.quality
