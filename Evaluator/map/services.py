#-*- coding: utf-8 -*-
import regions.services as region_services
import layers.services as layer_services
from layers.models import Feature
from map.utils import polygons_to_mpoly
from django.core.cache import cache
from random import shuffle


def get_points_by_policy(policy_name):
    chunk_num = 0
    point_cache = cache.get(' '.join(('policy', policy_name, str(chunk_num))).replace(' ', '_'))
    points = []
    while point_cache is not None:
	points.extend(point_cache)
	chunk_num += 1
	point_cache = cache.get(' '.join(('policy', policy_name, str(chunk_num))).replace(' ', '_'))
	
    if not points:
        polygons = region_services.get_policy_area_polygons(policy_name)
	mpoly = polygons_to_mpoly(polygons)
        points = layer_services.get_points_by_polygons(mpoly)
	# Store and load this in chunks
	for idx, chunk in enumerate([points[i:i+190000] for i in range(0, len(points), 190000)]):
	        cache.set(' '.join(('policy', policy_name, str(idx))).replace(' ', '_'), chunk, None)
		assert cache.has_key(' '.join(('policy', policy_name, str(idx))).replace(' ', '_')), "Could not write to cache"
    return points


def clear_cache_points_by_policy(policy_name):
    chunk_num = 0
    policy_key = ' '.join(('policy',policy_name,str(chunk_num))).replace(' ', '_')
    while cache.has_key(policy_key):
        cache.delete(policy_key)
	chunk_num +=1
        policy_key = ' '.join(('policy',policy_name,str(chunk_num))).replace(' ', '_')


def get_points_by_region(fid):
    feature_ids = cache.get(' '.join(('region', fid)).replace(' ', '_'))
    if feature_ids is None:
        multipolygon = region_services.get_region_polygon(fid)
        country = region_services.get_region_country(fid)

        feature_ids = list(
                Feature.objects
                    .filter(geom_point__within=multipolygon)
                    .values_list('id', flat=True))
        cache.set(' '.join(('region', fid)).replace(' ', '_'), feature_ids, None)
    return feature_ids


def clear_cache_points_by_region(fid):
    region_key = ' '.join(('region', fid)).replace(' ', '_')
    if cache.has_key(region_key):
        cache.delete(region_key)
