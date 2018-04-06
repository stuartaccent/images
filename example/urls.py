from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from example.views import ImageList

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ImageList.as_view())
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
