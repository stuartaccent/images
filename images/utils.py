import logging

from images.conf import get_setting
from images.exceptions import SourceImageIOError


logger = logging.getLogger(__name__)


def create_default_image_renditions(instance):
    """ create default renditions for an image instance """

    # if required delete all the renditions on save
    if get_setting('CLEAR_RENDITIONS_ON_SAVE'):
        instance.renditions.all().delete()

    try:
        # create a rendition for each of the defaults
        for filter_spec in get_setting('DEFAULT_FILTER_SPECS'):
            instance.get_rendition(filter_spec)

        # create the thumbnail rendition
        thumbnail_spec = get_setting('THUMBNAIL_FILTER_SPEC')
        if thumbnail_spec:
            instance.get_rendition(thumbnail_spec)

    except SourceImageIOError:
        logger.error('Source image missing {}'.format(instance))


def parse_color_string(color_string):
    """
    Parses a string a user typed into a tuple of 3 integers representing the
    red, green and blue channels respectively.
    May raise a ValueError if the string cannot be parsed.
    The colour string must be a CSS 3 or 6 digit hex code without the '#' prefix.
    """

    if len(color_string) == 3:
        r = int(color_string[0], 16) * 17
        g = int(color_string[1], 16) * 17
        b = int(color_string[2], 16) * 17
    elif len(color_string) == 6:
        r = int(color_string[0:2], 16)
        g = int(color_string[2:4], 16)
        b = int(color_string[4:6], 16)
    else:
        ValueError('Color string must be either 3 or 6 hexadecimal digits long')

    return r, g, b
