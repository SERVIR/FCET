from django.test import TestCase
from map.models import Map
from map.utils import geojson_to_polygons
from django.contrib.auth.models import User
from layers.models import Feature

class MapTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='test')        
        
    def test_map_collectfeatures(self):
        user = User.objects.get(username='test')
        Map.objects.create(user=user)
        features = Feature.objects.order_by('id').all()
        user.map.featurestatus_set.collect_features(user.map, features, 500)

    #def test_user_hasnomap_is_graceful(self):
    #    user = User.objects.get(username='test')
    #    user.map.collect_features()
        
class MapUtilsTestCase(TestCase):
    def test_empty_geojson_to_polygon(self):
        json = ''        
        with self.assertRaisesMessage(ValueError, 'Json string is empty'):
            geojson_to_polygons(json, 900913, 4326)
                                         
    def test_single_geojson_to_polygon(self):
        json = """{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-13018143.159491,3811914.6000511],[-12961274.010455,3792958.217039],[-13004690.242515,3778282.3076103],[-13018143.159491,3811914.6000511]]]},"crs":{"type":"name","properties":{"name":"EPSG:900913"}}}"""
        #json = '{"type":"Polygon","coordinates":[[[-13018143.159491,3811914.6000511],[-12961274.010455,3792958.217039],[-13004690.242515,3778282.3076103],[-13018143.159491,3811914.6000511]]]}'        
        geojson_to_polygons(json, 900913, 4326)
        
    def test_multi_geojson_to_polygons(self):
        json = """{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-13018143.159491,3811914.6000511],[-12961274.010455,3792958.217039],[-13004690.242515,3778282.3076103],[-13018143.159491,3811914.6000511]]]}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-12949044.085931,3729362.6095146],[-12936814.161407,3784397.2698722],[-12887282.967085,3770332.8566697],[-12897678.402931,3719578.6698954],[-12949044.085931,3729362.6095146]]]}}]}"""
        #json = '{"type":"Polygon","coordinates":[[[-13018143.159491,3811914.6000511],[-12961274.010455,3792958.217039],[-13004690.242515,3778282.3076103],[-13018143.159491,3811914.6000511]]]}},{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-12949044.085931,3729362.6095146],[-12936814.161407,3784397.2698722],[-12887282.967085,3770332.8566697],[-12897678.402931,3719578.6698954],[-12949044.085931,3729362.6095146]]]}}]}'
        polygons = geojson_to_polygons(json, 900913, 4326)
        self.assertEqual(len(list(polygons)), 2)