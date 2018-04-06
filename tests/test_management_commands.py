from django.core.management import call_command
from django.test import TestCase, override_settings

from images.models import Image
from tests.data import get_temporary_image


class CommandsTestCase(TestCase):
    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=['width-100', 'width-200'])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC='width-50')
    def test_regenerate_renditions(self):
        self.image.renditions.all().delete()

        self.assertEqual(self.image.renditions.count(), 0)

        args = []
        opts = {}
        call_command('regenerate_renditions', *args, **opts)

        self.assertEqual(self.image.renditions.count(), 3)
