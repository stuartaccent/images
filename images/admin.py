from django.contrib import admin
from django.utils.safestring import mark_safe

from images.forms import ImageForm
from images.models import Image, Rendition
from images.shortcuts import get_rendition_or_not_found


class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'preview', 'width', 'height']
    form = ImageForm
    readonly_fields = ['width', 'height']

    class Media:
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js',
            'images/js/jquery.ba-throttle-debounce.min.js',
            'images/js/Jcrop.min.js',
            'images/js/auto-title.js',
            'images/js/focal-point-chooser.js'
        )
        css = {
            'all': (
                'images/css/Jcrop.min.css',
                'images/css/focal-point-chooser.css'
            )
        }

    def preview(self, obj):
        orig = get_rendition_or_not_found(obj, 'original')
        thumb = get_rendition_or_not_found(obj, 'thumbnail')

        html = """
        <a href="{}"><img src="{}" alt="{}"></a>
        """.format(orig.url, thumb.url, thumb.alt)

        return mark_safe(html)


class RenditionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'file', 'width', 'height', 'filter_spec']
    readonly_fields = ['image', 'file', 'width', 'height', 'filter_spec']

    def has_add_permission(self, request):
        return False


admin.site.register(Image, ImageAdmin)
admin.site.register(Rendition, RenditionAdmin)
