from django.core.management.base import BaseCommand, CommandError
from regions.models import PolicyArea
from regions.views import _load_shapefile


class Command(BaseCommand):
    help = 'Upload a shapefile to be used as a policy area'

    def add_arguments(self, parser):
        parser.add_argument('shapefile', nargs='+', type=str)

    def handle(self, *args, **options):
        shapefile_name = options['shapefile'][0]
        _load_shapefile(shapefile_name)
