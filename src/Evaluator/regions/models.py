from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.gis import geos
from django.core import serializers
import json

class RegionManager(geomodels.Manager):
    def as_json(self):
        """
        Get heirachy of regions with related polygons
        :return: JSON-response
        """
        # It would be good to rewrite this function for N-nested levels eventually
        region_features = Region.objects.all()
        # Create a B-tree/JSON representation of the Region table
        countries = {}
        for region in region_features:
            # This recursive logic can be tricky ...
            # Sock goes on foot, shoe goes on sock, never in any other order
            # It may also help to read this from the bottom up
            # This is essentially a B-tree depth first traversal
            country = countries.setdefault(region.country, {'sub_regions': {}})
            sub_region = country['sub_regions'].setdefault(region.sub_region, {'regions': {}})
            sub_region['regions'].setdefault(region.region, {'bounds':region.get_bounds()})
        #Consider splitting these into two functions or methods
        # Unfortunately, to get this representation into ExtJs we need to convert countries, sub-regions
        # and regions into lists

        # This is actually three nested for loops, but the inner-most loop is written as a comprehension
        # For representation in ExtJs we require both a numerical id and a name, however the id can be somewhat arbitrary

        country_list = []
        for country_id, (country, items) in enumerate(countries.items()):
            sub_region_list = []
            sub_regions = items['sub_regions']
            for sub_region_id, (sub_region, items) in enumerate(sub_regions.items()):
                regions = items['regions']
                region_list = [{'id': region_id, 'name': region, 'bounds':items['bounds']}
                               for region_id, (region, items)
                               in enumerate(regions.items())]

                sub_region_list.append({'id': sub_region_id, 'name':sub_region, 'regions':region_list})
            country_list.append({'id': country_id, 'name': country, 'sub_regions': sub_region_list})

        countries = {'countries': country_list}
        # The database is currently in latin1/ISO-8859-1 encoding -- this should be changed
        # We need to make sure Python uses the correct encoding and that the http content type also
        # shows the correct encoding
        json_response = json.dumps(countries, ensure_ascii=False).encode('latin1')
        return json_response

    def as_unested_json(self):
        region_features = Region.objects.all()
        return serializers.serialize('geojson', region_features,
                                     geometry_field='poly',
                                     fields=('poly', 'country', 'sub_region', 'region')).encode('latin1')

class Region(geomodels.Model):
    """
    Model to store polygons for geographic regions
    """
    country = models.CharField(max_length=128)
    sub_region = models.CharField(max_length=128, null=True)
    region = models.CharField(max_length=128)
    poly = geomodels.MultiPolygonField(srid=4326, blank=True)
    bbox = models.CharField(max_length=255, null=True)
    objects = RegionManager()

    def get_bounds(self):
        """
        Retrieve the bounding box for a given region

        :return: GeoDjango extent as tuple
        """
        return self.poly.extent


class PolicyArea(geomodels.Model):
    """
    Store multipolygons for known policy areas to be used a treatment area selections in the tool
    """
    name = models.CharField(max_length=128)
    poly = geomodels.MultiPolygonField(srid=4326, blank=True)
    shapefile_name = models.CharField(max_length=128)
