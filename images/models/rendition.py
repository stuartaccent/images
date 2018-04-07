from collections import OrderedDict

from django.db import models
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class AbstractRendition(models.Model):
    """ Abstract base model to hold various renditions of an image """

    filter_spec = models.CharField(
        max_length=255,
        db_index=True
    )
    image = models.ForeignKey(
        'Image',
        related_name='renditions',
        on_delete=models.CASCADE
    )
    file = models.ImageField(
        verbose_name=_('file'),
        upload_to='images_renditions/',
        width_field='width',
        height_field='height'
    )
    width = models.IntegerField(
        verbose_name=_('width'),
        editable=False
    )
    height = models.IntegerField(
        verbose_name=_('height'),
        editable=False
    )
    focal_point_key = models.CharField(
        max_length=16,
        blank=True,
        default='',
        editable=False
    )

    class Meta:
        abstract = True
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

    @property
    def url(self):
        return self.file.url

    @property
    def alt(self):
        return self.image.title

    @property
    def attrs(self):
        """
        The src, width, height, and alt attributes for an <img> tag, as a HTML
        string
        """
        return flatatt(self.attrs_dict)

    @property
    def attrs_dict(self):
        """
        A dict of the src, width, height, and alt attributes for an <img> tag.
        """
        return OrderedDict([
            ('src', self.url),
            ('width', self.width),
            ('height', self.height),
            ('alt', self.alt),
        ])

    def img_tag(self, extra_attributes={}):
        attrs = self.attrs_dict.copy()
        attrs.update(extra_attributes)
        return mark_safe('<img{}>'.format(flatatt(attrs)))


class Rendition(AbstractRendition):
    """ hold various renditions of an image """
