from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image


def get_temporary_image():
    io = BytesIO()
    size = (400, 200)
    color = (255, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(io, format='JPEG')
    image_file = InMemoryUploadedFile(io, None, 'image.jpg', 'jpeg', len(io.getvalue()), None)
    image_file.seek(0)
    return image_file
