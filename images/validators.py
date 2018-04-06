import os

from django.core.exceptions import ValidationError

from images.conf import get_setting


def validate_image_file_extension(value):
    if not value:
        return
    allowed = get_setting('ALLOWED_FILE_EXTENSIONS')
    ext = os.path.splitext(value.name)[1]
    ext = ext.lower()
    if ext not in allowed:
        raise ValidationError("Unsupported file type, please use one of %s" % ', '.join(allowed))
