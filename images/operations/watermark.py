from PIL import Image, ImageEnhance

from images.conf import get_setting
from .base import Operation


class WatermarkOperation(Operation):
    watermark_path = get_setting('WATERMARK_IMAGE_PATH')
    margin = 10
    opacity = get_setting('WATERMARK_IMAGE_OPACITY')

    def construct(self, size):
        width_str, height_str = size.split('x')
        self.width = int(width_str)
        self.height = int(height_str)

    def run(self, willow, image, env):
        image_width, image_height = willow.get_size()

        watermark = Image.open(self.watermark_path)
        watermark_width, watermark_height = watermark.size

        horz_scale = self.width / watermark_width
        vert_scale = self.height / watermark_height

        if watermark_width <= self.width and watermark_height <= self.height:
            pass

        else:

            if horz_scale < vert_scale:
                width = self.width
                height = int(watermark_height * horz_scale)
            else:
                width = int(watermark_width * vert_scale)
                height = self.height

            watermark = watermark.resize((width, height), Image.ANTIALIAS)

        offset_x = (image_width - watermark.size[0]) - self.margin
        offset_y = (image_height - watermark.size[1]) - self.margin

        manipulated_image = Image.new('RGBA', (image_width, image_height), (255, 255, 255, 1))
        manipulated_image.paste(watermark, (offset_x, offset_y), mask=watermark.split()[3])

        alpha = manipulated_image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity)

        manipulated_image.putalpha(alpha)

        willow.image = Image.composite(manipulated_image, willow.image, manipulated_image)

        return willow
