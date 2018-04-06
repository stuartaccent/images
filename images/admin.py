from django.contrib import admin
from django.utils.safestring import mark_safe

from images.conf import get_setting
from images.models import Image, Rendition
from images.shortcuts import get_rendition_or_not_found


class ImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'preview', 'width', 'height', 'created_at']
    readonly_fields = ['width', 'height', 'created_at']

    class Media:
        js = (
            'images/js/auto-title.js',
        )

    def preview(self, obj):
        orig = get_rendition_or_not_found(obj, 'original')
        thumb = get_rendition_or_not_found(obj, 'thumbnail')

        html = """<a href="{}"><img src="{}" alt="{}"></a>""".format(orig.url, thumb.url, thumb.alt)

        return mark_safe(html)


class RenditionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'preview', 'width', 'height', 'filter_spec']
    readonly_fields = ['width', 'height', 'filter_spec']

    def has_add_permission(self, request):
        return False

    def preview(self, obj):
        thumb = get_rendition_or_not_found(obj.image, 'thumbnail')

        html = """<a href="{}"><img src="{}" alt="{}"></a>""".format(obj.url, thumb.url, thumb.alt)

        return mark_safe(html)


admin.site.register(Image, ImageAdmin)
admin.site.register(Rendition, RenditionAdmin)
