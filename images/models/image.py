from contextlib import contextmanager
from io import BytesIO
import os

from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.db import models
from django.utils.translation import ugettext_lazy as _

from willow.image import Image as WillowImage

from images.exceptions import SourceImageIOError
from images.filter import Filter
from images.rect import Rect
from images.validators import validate_image_file_extension


class AbstractImage(models.Model):
    """ abstract base image model to hold images and which to create renditions from. """

    title = models.CharField(
        max_length=255,
        verbose_name=_('title')
    )
    file = models.ImageField(
        verbose_name=_('file'),
        upload_to='original_images/',
        width_field='width',
        height_field='height',
        validators=[validate_image_file_extension]
    )
    width = models.IntegerField(
        verbose_name=_('width'),
        editable=False
    )
    height = models.IntegerField(
        verbose_name=_('height'),
        editable=False
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
        db_index=True
    )
    focal_point_x = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    focal_point_y = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    focal_point_width = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    focal_point_height = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def is_stored_locally(self):
        """ Returns True if the image is hosted on the local filesystem """
        try:
            self.file.path

            return True
        except NotImplementedError:
            return False

    @contextmanager
    def get_willow_image(self):
        # Open file if it is closed
        close_file = False
        try:
            image_file = self.file

            if self.file.closed:
                # Reopen the file
                if self.is_stored_locally():
                    self.file.open('rb')
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance. #1397
                    storage = self._meta.get_field('file').storage
                    image_file = storage.open(self.file.name, 'rb')

                close_file = True
        except IOError as e:
            # re-throw this as a SourceImageIOError so that calling code can distinguish
            # these from IOErrors elsewhere in the process
            raise SourceImageIOError(str(e))

        # Seek to beginning
        image_file.seek(0)

        try:
            yield WillowImage.open(image_file)
        finally:
            if close_file:
                image_file.close()

    def get_rect(self):
        return Rect(0, 0, self.width, self.height)

    def get_focal_point(self):
        if self.focal_point_x is not None and self.focal_point_y is not None and \
                self.focal_point_width is not None and self.focal_point_height is not None:
            return Rect.from_point(
                self.focal_point_x,
                self.focal_point_y,
                self.focal_point_width,
                self.focal_point_height,
            )

    def has_focal_point(self):
        return self.get_focal_point() is not None

    def set_focal_point(self, rect):
        if rect is not None:
            self.focal_point_x = rect.centroid_x
            self.focal_point_y = rect.centroid_y
            self.focal_point_width = rect.width
            self.focal_point_height = rect.height
        else:
            self.focal_point_x = None
            self.focal_point_y = None
            self.focal_point_width = None
            self.focal_point_height = None

    def get_rendition(self, filter):
        if isinstance(filter, str):
            filter = Filter(spec=filter)

        cache_key = filter.get_cache_key(self)

        try:
            rendition = self.renditions.get(
                filter_spec=filter.spec,
                focal_point_key=cache_key
            )
        except ObjectDoesNotExist:
            # Generate the rendition image
            generated_image = filter.run(self, BytesIO())

            # Generate filename
            input_filename = os.path.basename(self.file.name)
            input_filename_without_extension, input_extension = os.path.splitext(input_filename)

            format_mapping = {
                'jpeg': '.jpg',
                'png': '.png',
                'gif': '.gif',
            }

            # Get the file extension to output
            output_extension = filter.spec.replace('|', '.') + format_mapping[generated_image.format_name]

            # Truncate filename to prevent it going over 60 chars
            output_filename_without_extension = input_filename_without_extension[:(59 - len(output_extension))]
            output_filename = output_filename_without_extension + '.' + output_extension

            rendition, created = self.renditions.get_or_create(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
                defaults={'file': File(generated_image.f, name=output_filename)}
            )

        return rendition


class Image(AbstractImage):
    """ base image model """
