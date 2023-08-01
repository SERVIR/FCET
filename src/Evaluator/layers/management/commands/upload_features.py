from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Upload a shapefile to be dissolved into features and store attribute in an entity attribute value table.'

    def add_arguments(self, parser):
        parser.add_argument('shapefile_location', nargs='+', type=str)
        parser.add_argument('slice_stop', nargs='+', type=str)

    def handle(self, *args, **options):
        shapefile_location = options['shapefile_location'][0]
        slice_stop = options['slice_stop'][0]
        slice_stop = None if slice_stop == "None" else int(slice_stop)
        user = User.objects.filter(username='test')[0]
        upload = user.upload_set.create(geom_type='geom', encoding='enc')
        upload.upload_features(shapefile_location, slice_stop=slice_stop)
