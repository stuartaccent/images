from django.db import transaction
from django.test import TransactionTestCase

from images.models import Image
from tests.data import get_temporary_image


class TestFilesDeletedForDefaultModels(TransactionTestCase):
    def test_image_file_deleted_oncommit(self):
        with transaction.atomic():
            image = Image.objects.create(title="Test Image", file=get_temporary_image())
            self.assertTrue(image.file.storage.exists(image.file.name))
            image.delete()
            self.assertTrue(image.file.storage.exists(image.file.name))
        self.assertFalse(image.file.storage.exists(image.file.name))

    def test_rendition_file_deleted_oncommit(self):
        with transaction.atomic():
            image = Image.objects.create(title="Test Image", file=get_temporary_image())
            rendition = image.get_rendition('original')
            self.assertTrue(rendition.file.storage.exists(rendition.file.name))
            rendition.delete()
            self.assertTrue(rendition.file.storage.exists(rendition.file.name))
        self.assertFalse(rendition.file.storage.exists(rendition.file.name))
