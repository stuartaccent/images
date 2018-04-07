import os
from django.db import models
from django.test import override_settings

from images.models import Image
from images.rect import Rect
from images.validators import validate_image_file_extension
from tests.data import get_temporary_image
from tests.test_case import AppTestCase


class ModelTests(AppTestCase):

    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(size=(640, 480)),
        )

    # fields

    def test_title(self):
        field = Image._meta.get_field('title')
        self.assertModelField(field, models.CharField)
        self.assertEqual(field.max_length, 255)

    def test_file(self):
        field = Image._meta.get_field('file')
        self.assertModelField(field, models.ImageField)
        self.assertEqual(field.upload_to, 'original_images/')
        self.assertEqual(field.width_field, 'width')
        self.assertEqual(field.height_field, 'height')
        self.assertListEqual(field.validators, [validate_image_file_extension])

    def test_width(self):
        field = Image._meta.get_field('width')
        self.assertModelField(field, models.IntegerField)
        self.assertFalse(field.editable)

    def test_height(self):
        field = Image._meta.get_field('height')
        self.assertModelField(field, models.IntegerField)
        self.assertFalse(field.editable)

    def test_created_at(self):
        field = Image._meta.get_field('created_at')
        self.assertModelField(field, models.DateTimeField, blank=True)
        self.assertTrue(field.auto_now_add)

    def test_focal_point_x(self):
        field = Image._meta.get_field('focal_point_x')
        self.assertModelField(field, models.PositiveIntegerField, True, True)

    def test_focal_point_y(self):
        field = Image._meta.get_field('focal_point_y')
        self.assertModelField(field, models.PositiveIntegerField, True, True)

    def test_focal_point_width(self):
        field = Image._meta.get_field('focal_point_width')
        self.assertModelField(field, models.PositiveIntegerField, True, True)

    def test_focal_point_height(self):
        field = Image._meta.get_field('focal_point_height')
        self.assertModelField(field, models.PositiveIntegerField, True, True)

    # properties

    def test_get_rect(self):
        self.assertTrue(self.image.get_rect(), Rect(0, 0, 640, 480))

    def test_get_focal_point(self):
        self.assertEqual(self.image.get_focal_point(), None)

        # Add a focal point to the image
        self.image.focal_point_x = 100
        self.image.focal_point_y = 200
        self.image.focal_point_width = 50
        self.image.focal_point_height = 20

        # Get it
        self.assertEqual(self.image.get_focal_point(), Rect(75, 190, 125, 210))

    def test_has_focal_point(self):
        self.assertFalse(self.image.has_focal_point())

        # Add a focal point to the image
        self.image.focal_point_x = 100
        self.image.focal_point_y = 200
        self.image.focal_point_width = 50
        self.image.focal_point_height = 20

        self.assertTrue(self.image.has_focal_point())

    def test_set_focal_point(self):
        self.assertEqual(self.image.focal_point_x, None)
        self.assertEqual(self.image.focal_point_y, None)
        self.assertEqual(self.image.focal_point_width, None)
        self.assertEqual(self.image.focal_point_height, None)

        self.image.set_focal_point(Rect(100, 150, 200, 350))

        self.assertEqual(self.image.focal_point_x, 150)
        self.assertEqual(self.image.focal_point_y, 250)
        self.assertEqual(self.image.focal_point_width, 100)
        self.assertEqual(self.image.focal_point_height, 200)

        self.image.set_focal_point(None)

        self.assertEqual(self.image.focal_point_x, None)
        self.assertEqual(self.image.focal_point_y, None)
        self.assertEqual(self.image.focal_point_width, None)
        self.assertEqual(self.image.focal_point_height, None)

    def test_is_stored_locally(self):
        self.assertTrue(self.image.is_stored_locally())


class GetRenditionTests(AppTestCase):

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=['width-100', 'width-200'])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_default_renditions_are_created(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        self.assertEqual(image.renditions.count(), 2)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC='width-100')
    def test_thumbnail_rendition_is_created(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        self.assertEqual(image.renditions.count(), 1)


    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_no_default_renditions_are_created(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        self.assertEqual(image.renditions.count(), 0)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=['width-100', ])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    @override_settings(IMAGES_CLEAR_RENDITIONS_ON_SAVE=True)
    def test_clears_renditions_on_save(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        image.get_rendition('width-50')
        image.get_rendition('width-150')

        self.assertEqual(image.renditions.count(), 3)

        image.save()

        self.assertEqual(image.renditions.count(), 1)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_original(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        filter_spec = 'original'
        rendition = image.get_rendition(filter_spec)

        # should have one rendition
        self.assertEqual(image.renditions.count(), 1)

        image_filename = os.path.basename(image.file.name)
        image_filename_without_extension, image_extension = os.path.splitext(image_filename)

        rendition_filename = os.path.basename(rendition.file.name)

        self.assertEqual(
            rendition_filename,
            '%s.%s%s' % (image_filename_without_extension, filter_spec, image_extension)
        )

        self.assertEqual(rendition.file.width, image.file.width)
        self.assertEqual(rendition.file.height, image.file.height)
        self.assertEqual(rendition.filter_spec, filter_spec)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_height(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        filter_spec = 'height-100'
        rendition = image.get_rendition(filter_spec)

        # should have one rendition
        self.assertEqual(image.renditions.count(), 1)

        image_filename = os.path.basename(image.file.name)
        image_filename_without_extension, image_extension = os.path.splitext(image_filename)

        rendition_filename = os.path.basename(rendition.file.name)

        self.assertEqual(
            rendition_filename,
            '%s.%s%s' % (image_filename_without_extension, filter_spec, image_extension)
        )

        # original image is 400x200
        self.assertEqual(rendition.file.width, 200)
        self.assertEqual(rendition.file.height, 100)
        self.assertEqual(rendition.filter_spec, filter_spec)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_width(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        filter_spec = 'width-100'
        rendition = image.get_rendition(filter_spec)

        # should have one rendition
        self.assertEqual(image.renditions.count(), 1)

        image_filename = os.path.basename(image.file.name)
        image_filename_without_extension, image_extension = os.path.splitext(image_filename)

        rendition_filename = os.path.basename(rendition.file.name)

        self.assertEqual(
            rendition_filename,
            '%s.%s%s' % (image_filename_without_extension, filter_spec, image_extension)
        )

        # original image is 400x200
        self.assertEqual(rendition.file.width, 100)
        self.assertEqual(rendition.file.height, 50)
        self.assertEqual(rendition.filter_spec, filter_spec)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_width_and_height(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        filter_spec = 'width-100|height-100'
        rendition = image.get_rendition(filter_spec)

        # should have one rendition
        self.assertEqual(image.renditions.count(), 1)

        image_filename = os.path.basename(image.file.name)
        image_filename_without_extension, image_extension = os.path.splitext(image_filename)

        rendition_filename = os.path.basename(rendition.file.name)

        self.assertEqual(
            rendition_filename,
            '%s.%s%s' % (image_filename_without_extension, filter_spec.replace('|', '.'), image_extension)
        )

        # original image is 400x200 will result in 100x50 so to not screw up image ratio
        self.assertEqual(rendition.file.width, 100)
        self.assertEqual(rendition.file.height, 50)
        self.assertEqual(rendition.filter_spec, filter_spec)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_width_and_height__wont_stretch_original_image_size(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        filter_spec = 'width-1000|height-1000'
        rendition = image.get_rendition(filter_spec)

        self.assertEqual(image.renditions.count(), 1)

        image_filename = os.path.basename(image.file.name)
        image_filename_without_extension, image_extension = os.path.splitext(image_filename)

        rendition_filename = os.path.basename(rendition.file.name)

        self.assertEqual(
            rendition_filename,
            '%s.%s%s' % (image_filename_without_extension, filter_spec.replace('|', '.'), image_extension)
        )

        # original image is 400x200
        self.assertEqual(rendition.file.width, image.file.width)
        self.assertEqual(rendition.file.height, image.file.height)
        self.assertEqual(rendition.filter_spec, filter_spec)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_each_filter__should_create_its_own_rendition(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        image.get_rendition('original')
        image.get_rendition('height-100')
        image.get_rendition('width-100')

        # should have three renditions
        self.assertEqual(image.renditions.count(), 3)

    @override_settings(IMAGES_DEFAULT_FILTER_SPECS=[])
    @override_settings(IMAGES_THUMBNAIL_FILTER_SPEC=None)
    def test_same_filter_called_twice__should_not_create_another_rendition(self):
        image = Image.objects.create(
            title='Some Title',
            file=get_temporary_image()
        )
        image.get_rendition('original')
        image.get_rendition('original')

        # should have one rendition
        self.assertEqual(image.renditions.count(), 1)
