from django.test import TestCase

from images.models import Image
from images.shortcuts import get_rendition_or_not_found

from .data import get_temporary_image


class TestShortcuts(TestCase):
    fixtures = ['test']

    def test_fallback_to_not_found(self):
        bad_image = Image.objects.get(pk=1)
        good_image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        rendition = get_rendition_or_not_found(good_image, 'width-400')
        self.assertEqual(rendition.width, 400)

        rendition = get_rendition_or_not_found(bad_image, 'width-400')
        self.assertEqual(rendition.file.name, 'not-found')
