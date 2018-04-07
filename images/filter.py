import hashlib

from django.utils.functional import cached_property

from images import image_operations
from images.conf import get_setting
from images.exceptions import InvalidFilterSpecError


class Filter:
    def __init__(self, spec=None):
        self.spec = spec

    @cached_property
    def operations(self):
        # Search for operations
        self._search_for_operations()

        # Build list of operation objects
        operations = []

        # if a thumbnail is requested replace the spec with the deftault spec for a thumbnail
        if 'thumbnail' in self.spec:
            self.spec = self.spec.replace('thumbnail', get_setting('THUMBNAIL_FILTER_SPEC'))

        # ensure all requested specs are valid and build the list of operations
        for op_spec in self.spec.split('|'):
            op_spec_parts = op_spec.split('-')

            if op_spec_parts[0] not in self._registered_operations:
                raise InvalidFilterSpecError("Unrecognised operation: %s" % op_spec_parts[0])

            op_class = self._registered_operations[op_spec_parts[0]]
            operations.append(op_class(*op_spec_parts))
        return operations

    def run(self, image, output):
        with image.get_willow_image() as willow:
            original_format = willow.format_name

            # Fix orientation of image
            willow = willow.auto_orient()

            env = {
                'original-format': original_format,
            }

            for operation in self.operations:
                willow = operation.run(willow, image, env) or willow

            if 'output-format' in env:
                # Developer specified an output format
                output_format = env['output-format']

            else:
                # Default to outputting in original format
                output_format = original_format

                # Convert unanimated GIFs to PNG as well
                if original_format == 'gif' and not willow.has_animation():
                    output_format = 'png'

            if output_format == 'jpeg':
                # set the quality
                if 'jpeg-quality' in env:
                    quality = env['jpeg-quality']
                else:
                    quality = get_setting('JPG_QUALITY')

                # If the image has an alpha channel, give it a white background
                if willow.has_alpha():
                    willow = willow.set_background_color_rgb((255, 255, 255))

                return willow.save_as_jpeg(output, quality=quality, progressive=True, optimize=True)

            elif output_format == 'png':
                return willow.save_as_png(output)

            elif output_format == 'gif':
                return willow.save_as_gif(output)

    def get_cache_key(self, image):
        vary_parts = []

        for operation in self.operations:
            for field in getattr(operation, 'vary_fields', []):
                value = getattr(image, field, '')
                vary_parts.append(str(value))

        vary_string = '-'.join(vary_parts)

        # Return blank string if there are no vary fields
        if not vary_string:
            return ''

        return hashlib.sha1(vary_string.encode('utf-8')).hexdigest()[:8]

    _registered_operations = None

    @classmethod
    def _search_for_operations(cls):
        if cls._registered_operations is not None:
            return

        operations = [
            ('original', image_operations.DoNothingOperation),
            ('width', image_operations.WidthHeightOperation),
            ('height', image_operations.WidthHeightOperation),
            ('min', image_operations.MinMaxOperation),
            ('max', image_operations.MinMaxOperation),
            ('fill', image_operations.FillOperation),
            ('jpegquality', image_operations.JPEGQualityOperation),
            ('format', image_operations.FormatOperation),
        ]

        cls._registered_operations = dict(operations)
