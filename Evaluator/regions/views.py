from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.gis.utils import LayerMapping
from .models import Region
from django.contrib.gis.gdal import DataSource
import os
from django.core.cache import cache

def get_regions(request):
    regions = cache.get('evaluator_cache')
    if regions is None:
        regions = Region.objects.as_json()
        cache.set('evaluator_cache', regions, None)

    return HttpResponse(regions, content_type="application/json; charset=ISO-8859-1")

def get_all(request):
    regions = cache.get('all_regions')
    if regions is None:
        regions = Region.objects.as_unested_json()
        cache.set('all_regions', regions, None)

    return HttpResponse(regions, content_type="application/json; charset=ISO-8859-1")

def test_regions(request):
    # Actually this should be in layers
    """
    Loop through regions and attempt to query them for polygons to determine which ones are available
    :param request: Django Request Parameter
    :return: None
    """

# def _load_shapefile(country, sub_region, region):
def _load_shapefile(shapefile_name):
    """
    Load in shapefile to populate regions in the app
    :return: None
    """
    # Map shapefile variables to app variables
    country = 'NAME_0'
    sub_region = 'ENGTYPE_1'
    region = 'NAME_1'

    region_mapping = {
        'country': country,
        'sub_region': sub_region,
        'region': region,
        'poly': 'MULTIPOLYGON'
    }

    # Load shapefile and transfer to database
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', shapefile_name)) 
    ds = DataSource(data_path)

    lm = LayerMapping(Region, ds, region_mapping, transform=False, encoding='LATIN1')
    lm.save(strict=True)

    #Load regions into cache
    regions = Region.objects.as_json()
    cache.set('evaluator_cache', regions, None)
