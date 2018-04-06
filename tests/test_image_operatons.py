from io import BytesIO

from django.test import TestCase, override_settings
from mock import Mock, patch

from images import image_operations
from images.exceptions import InvalidFilterSpecError
from images.filter import Filter
from images.models import Image
from .data import get_temporary_image


class WillowOperationRecorder:
    """
    This class pretends to be a Willow image but instead, it records
    the operations that have been performed on the image for testing
    """
    format_name = 'jpeg'

    def __init__(self, start_size):
        self.ran_operations = []
        self.start_size = start_size

    def __getattr__(self, attr):
        def operation(*args, **kwargs):
            self.ran_operations.append((attr, args, kwargs))
            return self

        return operation

    def get_size(self):
        size = self.start_size

        for operation in self.ran_operations:
            if operation[0] == 'resize':
                size = operation[1][0]
            elif operation[0] == 'crop':
                crop = operation[1][0]
                size = crop[2] - crop[0], crop[3] - crop[1]

        return size


class ImageOperationTestCase(TestCase):
    operation_class = None
    filter_spec_tests = []
    filter_spec_error_tests = []
    run_tests = []

    @classmethod
    def make_filter_spec_test(cls, filter_spec, expected_output):
        def test_filter_spec(self):
            operation = self.operation_class(*filter_spec.split('-'))

            # Check the attributes are set correctly
            for attr, value in expected_output.items():
                self.assertEqual(getattr(operation, attr), value)

        test_filter_spec.__name__ = str('test_filter_%s' % filter_spec)
        return test_filter_spec

    @classmethod
    def make_filter_spec_error_test(cls, filter_spec):
        def test_filter_spec_error(self):
            self.assertRaises(InvalidFilterSpecError, self.operation_class, *filter_spec.split('-'))

        test_filter_spec_error.__name__ = str('test_filter_%s_raises_%s' % (
            filter_spec, InvalidFilterSpecError.__name__))
        return test_filter_spec_error

    @classmethod
    def make_run_test(cls, filter_spec, image_kwargs, expected_output):
        def test_run(self):
            image = Image(**image_kwargs)

            # Make operation
            operation = self.operation_class(*filter_spec.split('-'))

            # Make operation recorder
            operation_recorder = WillowOperationRecorder((image.width, image.height))

            # Run
            operation.run(operation_recorder, image, {})

            # Check
            self.assertEqual(operation_recorder.ran_operations, expected_output)

        test_run.__name__ = str('test_run_%s' % filter_spec)
        return test_run

    @classmethod
    def setup_test_methods(cls):
        if cls.operation_class is None:
            return

        # Filter spec tests
        for args in cls.filter_spec_tests:
            filter_spec_test = cls.make_filter_spec_test(*args)
            setattr(cls, filter_spec_test.__name__, filter_spec_test)

        # Filter spec error tests
        for filter_spec in cls.filter_spec_error_tests:
            filter_spec_error_test = cls.make_filter_spec_error_test(filter_spec)
            setattr(cls, filter_spec_error_test.__name__, filter_spec_error_test)

        # Running tests
        for args in cls.run_tests:
            run_test = cls.make_run_test(*args)
            setattr(cls, run_test.__name__, run_test)


class TestDoNothingOperation(ImageOperationTestCase):
    operation_class = image_operations.DoNothingOperation

    filter_spec_tests = [
        ('original', dict()),
        ('blahblahblah', dict()),
        ('123456', dict()),
    ]

    filter_spec_error_tests = [
        'cannot-take-multiple-parameters',
    ]

    run_tests = [
        ('original', dict(width=1000, height=1000), []),
    ]


TestDoNothingOperation.setup_test_methods()


class TestMinMaxOperation(ImageOperationTestCase):
    operation_class = image_operations.MinMaxOperation

    filter_spec_tests = [
        ('min-800x600', dict(method='min', width=800, height=600)),
        ('max-800x600', dict(method='max', width=800, height=600)),
    ]

    filter_spec_error_tests = [
        'min',
        'min-800',
        'min-abc',
        'min-800xabc',
        'min-800x600-',
        'min-800x600-c100',
        'min-800x600x10',
    ]

    run_tests = [
        # Basic usage of min
        ('min-800x600', dict(width=1000, height=1000), [
            ('resize', ((800, 800), ), {}),
        ]),
        # Basic usage of max
        ('max-800x600', dict(width=1000, height=1000), [
            ('resize', ((600, 600), ), {}),
        ]),
    ]


TestMinMaxOperation.setup_test_methods()


class TestWidthHeightOperation(ImageOperationTestCase):
    operation_class = image_operations.WidthHeightOperation

    filter_spec_tests = [
        ('width-800', dict(method='width', size=800)),
        ('height-600', dict(method='height', size=600)),
    ]

    filter_spec_error_tests = [
        'width',
        'width-800x600',
        'width-abc',
        'width-800-c100',
    ]

    run_tests = [
        # Basic usage of width
        ('width-400', dict(width=1000, height=500), [
            ('resize', ((400, 200), ), {}),
        ]),
        # Basic usage of height
        ('height-400', dict(width=1000, height=500), [
            ('resize', ((800, 400), ), {}),
        ]),
    ]


TestWidthHeightOperation.setup_test_methods()


class TestFormatFilter(TestCase):
    def test_jpeg(self):
        fil = Filter(spec='width-400|format-jpeg')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        out = fil.run(image, BytesIO())

        self.assertEqual(out.format_name, 'jpeg')

    def test_png(self):
        fil = Filter(spec='width-400|format-png')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        out = fil.run(image, BytesIO())

        self.assertEqual(out.format_name, 'png')

    def test_gif(self):
        fil = Filter(spec='width-400|format-gif')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        out = fil.run(image, BytesIO())

        self.assertEqual(out.format_name, 'gif')

    def test_invalid(self):
        fil = Filter(spec='width-400|format-foo')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())


class TestJPEGQualityFilter(TestCase):
    def test_default_quality(self):
        fil = Filter(spec='width-400')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', quality=85, optimize=True, progressive=True)

    def test_jpeg_quality_filter(self):
        fil = Filter(spec='width-400|jpegquality-40')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', quality=40, optimize=True, progressive=True)

    def test_jpeg_quality_filter_invalid(self):
        fil = Filter(spec='width-400|jpegquality-abc')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())

    def test_jpeg_quality_filter_no_value(self):
        fil = Filter(spec='width-400|jpegquality')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())

    def test_jpeg_quality_filter_too_big(self):
        fil = Filter(spec='width-400|jpegquality-101')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())

    @override_settings(IMAGES_JPG_QUALITY=50)
    def test_jpeg_quality_setting(self):
        fil = Filter(spec='width-400')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', quality=50, optimize=True, progressive=True)

    @override_settings(IMAGES_JPG_QUALITY=50)
    def test_jpeg_quality_filter_overrides_setting(self):
        fil = Filter(spec='width-400|jpegquality-40')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', quality=40, optimize=True, progressive=True)
