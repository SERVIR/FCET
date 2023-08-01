from django.core.management.base import BaseCommand, CommandError
from upload.views import test_file_upload
from Evaluator.settings import BASE_DIR
from layers.models import Feature, Attribute, AttributeValue
from django.db import connection
from layers.views import create_point_features
import os


class Command(BaseCommand):
    help = 'Upload shapefiles from layers/data to use as points in the app'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Searching layers/data for shapefiles")
        entries = [os.path.join(BASE_DIR, 'layers', 'data', entry)
                   for entry in
                   os.listdir(os.path.join(BASE_DIR, 'layers', 'data'))]

        directories = [entry
                       for entry in entries
                       if os.path.isdir(entry)]

        self.stdout.write('Found {} directories'.format(len(directories)))
        self.stdout.write('\n'.join([d for d in directories]))

        self.stdout.write('Removing onboard data')
        self.stdout.write('Deleting AttributeValues 1/3')
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM layers_attributevalue;')

        self.stdout.write('Deleting Features 2/3')
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM layers_feature;')

        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM layers_attribute_feature;')

        self.stdout.write('Deleting Attributes 3/3')
        with connection.cursor() as cursor:
            cursor.execute('DELETE FROM layers_attribute;')

        self.stdout.write('Writing shapefiles to database')
        for d in directories:
            # Find shapefile
            shapefile = [file for file in os.listdir(d) if file.endswith('.shp')][0]
            self.stdout.write('\n\nWriting {} to database\n\n'.format(shapefile))
            # Upload shapefile
            create_point_features(os.path.join(d, shapefile), None)

