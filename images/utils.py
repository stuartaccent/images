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
