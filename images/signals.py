from django.db import transaction
from django.db.models.signals import post_delete, post_save

from images.models import Image, Rendition
from images.utils import create_default_image_renditions


def create_image_renditions(instance, **kwargs):
    """ Create default image renditions """
    create_default_image_renditions(instance)


def delete_image_cleanup(instance, **kwargs):
    """ Cleanup deleted images from disk """
    transaction.on_commit(lambda: instance.file.delete(False))


def register_signals():
    post_save.connect(create_image_renditions, sender=Image)
    post_delete.connect(delete_image_cleanup, sender=Image)
    post_delete.connect(delete_image_cleanup, sender=Rendition)
