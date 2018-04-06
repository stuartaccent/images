from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImagesAppConfig(AppConfig):
    name = 'images'
    label = 'images'
    verbose_name = _("Images")

    def ready(self):
        from images.signals import register_signals
        register_signals()
