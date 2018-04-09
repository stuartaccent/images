from os.path import abspath, dirname

from django.conf import settings


SETTINGS_PREFIX = 'IMAGES'

SETTINGS_DEFAULTS = {
    'CLEAR_RENDITIONS_ON_SAVE': True,
    'DEFAULT_FILTER_SPECS': [
        'original',
    ],
    'JPG_QUALITY': 85,
    'ALLOWED_FILE_EXTENSIONS': [
        '.jpeg',
        '.jpg',
        '.png',
        '.gif'
    ],
    'THUMBNAIL_FILTER_SPEC': 'width-100',
    'WATERMARK_IMAGE_PATH': dirname(abspath(__file__)) + '/static/images/images/watermark.png',
    'WATERMARK_IMAGE_OPACITY': .5
}


def get_setting(name):
    setting_key = '{}_{}'.format(SETTINGS_PREFIX, name)
    return getattr(settings, setting_key, SETTINGS_DEFAULTS[name])
