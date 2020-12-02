from django.core.management.base import BaseCommand, CommandError
from regions.models import PolicyArea
from regions.services import _load_policy_area_shapefile


class Command(BaseCommand):
    help = 'Upload a shapefile to be used as a policy area'

    def add_arguments(self, parser):
        parser.add_argument('shapefile', nargs='+', type=str)
        parser.add_argument('policy_area_name', nargs='+', type=str)

    def handle(self, *args, **options):
        shapefile_name = options['shapefile'][0]
        policy_area_name = options['policy_area_name'][0]
        _load_policy_area_shapefile(shapefile_name, policy_area_name)
