from io import BytesIO

from django.test import TestCase, override_settings
from mock import Mock, patch

from images import operations
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
    operation_class = operations.DoNothingOperation

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


class TestFillOperation(ImageOperationTestCase):
    operation_class = operations.FillOperation

    filter_spec_tests = [
        ('fill-800x600', dict(width=800, height=600, crop_closeness=0)),
        ('hello-800x600', dict(width=800, height=600, crop_closeness=0)),
        ('fill-800x600-c0', dict(width=800, height=600, crop_closeness=0)),
        ('fill-800x600-c100', dict(width=800, height=600, crop_closeness=1)),
        ('fill-800x600-c50', dict(width=800, height=600, crop_closeness=0.5)),
        ('fill-800x600-c1000', dict(width=800, height=600, crop_closeness=1)),
        ('fill-800000x100', dict(width=800000, height=100, crop_closeness=0)),
    ]

    filter_spec_error_tests = [
        'fill',
        'fill-800',
        'fill-abc',
        'fill-800xabc',
        'fill-800x600-',
        'fill-800x600x10',
        'fill-800x600-d100',
    ]

    run_tests = [
        # Basic usage
        ('fill-800x600', dict(width=1000, height=1000), [
            ('crop', ((0, 125, 1000, 875), ), {}),
            ('resize', ((800, 600), ), {}),
        ]),

        # Basic usage with an oddly-sized original image
        # This checks for a rounding precision issue (#968)
        ('fill-200x200', dict(width=539, height=720), [
            ('crop', ((0, 90, 539, 630), ), {}),
            ('resize', ((200, 200), ), {}),
        ]),

        # Closeness shouldn't have any effect when used without a focal point
        ('fill-800x600-c100', dict(width=1000, height=1000), [
            ('crop', ((0, 125, 1000, 875), ), {}),
            ('resize', ((800, 600), ), {}),
        ]),

        # Should always crop towards focal point. Even if no closeness is set
        ('fill-80x60', dict(
            width=1000,
            height=1000,
            focal_point_x=1000,
            focal_point_y=500,
            focal_point_width=0,
            focal_point_height=0,
        ), [
            # Crop the largest possible crop box towards the focal point
            ('crop', ((0, 125, 1000, 875), ), {}),

            # Resize it down to final size
            ('resize', ((80, 60), ), {}),
        ]),

        # Should crop as close as possible without upscaling
        ('fill-80x60-c100', dict(
            width=1000,
            height=1000,
            focal_point_x=1000,
            focal_point_y=500,
            focal_point_width=0,
            focal_point_height=0,
        ), [
            # Crop as close as possible to the focal point
            ('crop', ((920, 470, 1000, 530), ), {}),

            # No need to resize, crop should've created an 80x60 image
        ]),

        # Ditto with a wide image
        # Using a different filter so method name doesn't clash
        ('fill-100x60-c100', dict(
            width=2000,
            height=1000,
            focal_point_x=2000,
            focal_point_y=500,
            focal_point_width=0,
            focal_point_height=0,
        ), [
            # Crop to the right hand side
            ('crop', ((1900, 470, 2000, 530), ), {}),
        ]),

        # Make sure that the crop box never enters the focal point
        ('fill-50x50-c100', dict(
            width=2000,
            height=1000,
            focal_point_x=1000,
            focal_point_y=500,
            focal_point_width=100,
            focal_point_height=20,
        ), [
            # Crop a 100x100 box around the entire focal point
            ('crop', ((950, 450, 1050, 550), ), {}),

            # Resize it down to 50x50
            ('resize', ((50, 50), ), {}),
        ]),

        # Test that the image is never upscaled
        ('fill-1000x800', dict(width=100, height=100), [
            ('crop', ((0, 10, 100, 90), ), {}),
        ]),

        # Test that the crop closeness gets capped to prevent upscaling
        ('fill-1000x800-c100', dict(
            width=1500,
            height=1000,
            focal_point_x=750,
            focal_point_y=500,
            focal_point_width=0,
            focal_point_height=0,
        ), [
            # Crop a 1000x800 square out of the image as close to the
            # focal point as possible. Will not zoom too far in to
            # prevent upscaling
            ('crop', ((250, 100, 1250, 900), ), {}),
        ]),

        # Test for an issue where a ZeroDivisionError would occur when the
        # focal point size, image size and filter size match
        # See: #797
        ('fill-1500x1500-c100', dict(
            width=1500,
            height=1500,
            focal_point_x=750,
            focal_point_y=750,
            focal_point_width=1500,
            focal_point_height=1500,
        ), [
            # This operation could probably be optimised out
            ('crop', ((0, 0, 1500, 1500), ), {}),
        ]),


        # A few tests for single pixel images

        ('fill-100x100', dict(
            width=1,
            height=1,
        ), [
            ('crop', ((0, 0, 1, 1), ), {}),
        ]),

        # This one once gave a ZeroDivisionError
        ('fill-100x150', dict(
            width=1,
            height=1,
        ), [
            ('crop', ((0, 0, 1, 1), ), {}),
        ]),

        ('fill-150x100', dict(
            width=1,
            height=1,
        ), [
            ('crop', ((0, 0, 1, 1), ), {}),
        ]),
    ]


TestFillOperation.setup_test_methods()


class TestMinMaxOperation(ImageOperationTestCase):
    operation_class = operations.MinMaxOperation

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
    operation_class = operations.WidthHeightOperation

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


class TestCropOperation(ImageOperationTestCase):
    operation_class = operations.CropOperation

    filter_spec_tests = [
        ('crop', dict()),
        ('crop-500x400x100x200', dict(left=500, top=400, width=100, height=200)),
    ]

    filter_spec_error_tests = [
        'crop-randomstring',
        'crop-100',
        'crop-100x100',
        'crop-100x100x100'
    ]

    run_tests = [
        # Should crop to focol points
        ('crop', dict(
            width=1000,
            height=1000,
            focal_point_x=500,
            focal_point_y=500,
            focal_point_width=500,
            focal_point_height=500,
        ), [
            ('crop', ((250, 250, 750, 750), ), {}),
        ]),

        # Should not crop if no focol points set
        ('crop', dict(
            width=1000,
            height=1000,
        ), []),

        # crop to center small size
        ('crop-500x500x100x100', dict(
            width=1000,
            height=1000,
        ), [
            ('crop', ((450, 450, 550, 550), ), {}),
        ]),

        # crop to center full size
        ('crop-500x500x1000x1000', dict(
            width=1000,
            height=1000,
        ), [
            ('crop', ((0, 0, 1000, 1000), ), {}),
        ]),

        # width greater than image keeps to image bounds
        ('crop-500x500x10000x1000', dict(
            width=1000,
            height=1000,
        ), [
            ('crop', ((0, 0, 1000, 1000), ), {}),
        ]),

        # height greater than image keeps to image bounds
        ('crop-500x500x1000x10000', dict(
            width=1000,
            height=1000,
        ), [
            ('crop', ((0, 0, 1000, 1000), ), {}),
        ]),

        # near edge allows only upto remaining image size
        ('crop-900x900x500x500', dict(
            width=1000,
            height=1000,
        ), [
            ('crop', ((800, 800, 1000, 1000), ), {}),
        ]),

        ('crop-100x100x500x500', dict(
            width=1000,
            height=1000,
        ), [
             ('crop', ((0, 0, 200, 200),), {}),
        ]),
    ]


TestCropOperation.setup_test_methods()


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
        fil = Filter(spec='width-400|format-jpeg')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', icc_profile=None, quality=85, optimize=True, progressive=True)

    def test_jpeg_quality_filter(self):
        fil = Filter(spec='width-400|format-jpeg|jpegquality-40')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', icc_profile=None, quality=40, optimize=True, progressive=True)

    def test_jpeg_quality_filter_invalid(self):
        fil = Filter(spec='width-400|format-jpeg|jpegquality-abc')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())

    def test_jpeg_quality_filter_no_value(self):
        fil = Filter(spec='width-400|format-jpeg|jpegquality')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())

    def test_jpeg_quality_filter_too_big(self):
        fil = Filter(spec='width-400|format-jpeg|jpegquality-101')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(InvalidFilterSpecError, fil.run, image, BytesIO())

    @override_settings(IMAGES_JPG_QUALITY=50)
    def test_jpeg_quality_setting(self):
        fil = Filter(spec='width-400|format-jpeg')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', icc_profile=None, quality=50, optimize=True, progressive=True)

    @override_settings(IMAGES_JPG_QUALITY=50)
    def test_jpeg_quality_filter_overrides_setting(self):
        fil = Filter(spec='width-400|format-jpeg|jpegquality-40')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

        f = BytesIO()
        with patch('PIL.Image.Image.save') as save:
            fil.run(image, f)

        save.assert_called_with(f, 'JPEG', icc_profile=None, quality=40, optimize=True, progressive=True)


class TestBackgroundColorFilter(TestCase):
    def test_original_has_alpha(self):
        # Checks that the test image we're using has alpha
        fil = Filter(spec='width-400')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        out = fil.run(image, BytesIO())

        self.assertTrue(out.has_alpha())

    def test_3_digit_hex(self):
        fil = Filter(spec='width-400|bgcolor-fff')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        out = fil.run(image, BytesIO())

        self.assertFalse(out.has_alpha())

    def test_6_digit_hex(self):
        fil = Filter(spec='width-400|bgcolor-ffffff')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        out = fil.run(image, BytesIO())

        self.assertFalse(out.has_alpha())

    def test_invalid(self):
        fil = Filter(spec='width-400|bgcolor-foo')
        image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )
        self.assertRaises(ValueError, fil.run, image, BytesIO())
