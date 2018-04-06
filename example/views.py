from django.views.generic import ListView

from images.models import Image


class ImageList(ListView):
    model = Image
