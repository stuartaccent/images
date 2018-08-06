from io import BytesIO

import PIL.Image
from django.core.files.images import ImageFile

from images.models import Image


def get_temporary_image(filename='image.png', colour='white', size=(400, 200)):
    f = BytesIO()
    image = PIL.Image.new('RGBA', size, colour)
    image.save(f, 'PNG')
    return ImageFile(f, name=filename)
