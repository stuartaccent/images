from django.core.management.base import BaseCommand

from images.models import Image
from images.utils import create_default_image_renditions


class Command(BaseCommand):
    help = 'Regenerate all default image renditions'

    def handle(self, *args, **options):
        done = 1
        image_count = Image.objects.count()
        for image in Image.objects.all():
            create_default_image_renditions(instance=image)
            self.stdout.write(self.style.SUCCESS('%s of %s Image(s)' % (done, image_count)))
            done += 1

        self.stdout.write(self.style.SUCCESS('Completed'))
