from django.db import models

from images.models import Image, Rendition
from tests.data import get_temporary_image
from tests.test_case import AppTestCase


class ModelTests(AppTestCase):

    # fields

    def test_image(self):
        field = Rendition._meta.get_field('image')
        self.assertModelPKField(field, Image, models.CASCADE, related_name='renditions')

    def test_file(self):
        field = Rendition._meta.get_field('file')
        self.assertModelField(field, models.ImageField)
        self.assertEqual(field.upload_to, 'images_renditions/')
        self.assertEqual(field.width_field, 'width')
        self.assertEqual(field.height_field, 'height')

    def test_width(self):
        field = Rendition._meta.get_field('width')
        self.assertModelField(field, models.IntegerField)
        self.assertFalse(field.editable)

    def test_height(self):
        field = Rendition._meta.get_field('height')
        self.assertModelField(field, models.IntegerField)
        self.assertFalse(field.editable)

    # props

    def test_url(self):
        image = Image.objects.create(title='Some Title', file=get_temporary_image())
        rendition = image.get_rendition('original')
        self.assertEqual(rendition.url, rendition.file.url)

    def test_alt(self):
        image = Image.objects.create(title='Some Title', file=get_temporary_image())
        rendition = image.get_rendition('original')
        self.assertEqual(rendition.alt, rendition.image.title)
