from django.test import TestCase
from map.models import Map
from map.utils import geojson_to_polygons, polygons_to_mpoly
from django.contrib.auth.models import User
from layers.models import Feature, FeatureStatus, AttributeValue
import django.contrib.gis.geos as geos
from itertools import chain


def create_points():
    p1, p2 = geos.Point(10, 10), geos.Point(11, 11)
    f1 = Feature.objects.create(geom_point=p1)
    f2 = Feature.objects.create(geom_point=p2)
    return (p1, p2, f1, f2)


def create_polygons():
    poly1 = geos.Polygon(((0, 0), (0, 50), (50, 50), (50, 0), (0, 0)))
    poly2 = geos.Polygon(((51, 51), (51, 60), (60, 60), (60, 51), (51, 51)))
    return (poly1, poly2)


class LayerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)

    def test_create_point(self):
        p = geos.Point((-12018143.159491, 3711914.6000511))
        Feature.objects.create(geom_point=p)

    def test_create_polygon(self):
        poly = geos.Polygon((
            (-13018143.159491, 3811914.6000511),
            (-12961274.010455, 3792958.217039),
            (-13004690.242515, 3778282.3076103),
            (-13018143.159491, 3811914.6000511)
        ))
        Feature.objects.create(geom_multipolygon=poly)

    def test_point_within_polygon(self):
        p = geos.Point(10, 10)
        poly = geos.Polygon(((0, 0), (0, 50), (50, 50), (50, 0), (0, 0)))
        Feature.objects.create(geom_point=p)
        features = Feature.objects.filter(geom_point__within=poly)[0]
        self.assertEqual(features.geom_point, p)

    def test_point_within_polygon_single(self):
        p = geos.Point(10, 10)
        poly = geos.Polygon(((0, 0), (0, 50), (50, 50), (50, 0), (0, 0)))
        Feature.objects.create(geom_point=p)
        features = Feature.objects.filter(geom_point__within=poly)
        self.assertEqual(len(features), 1)

    def test_point_within_polygon_double(self):
        create_points()
        poly = geos.Polygon(((0, 0), (0, 50), (50, 50), (50, 0), (0, 0)))
        features = Feature.objects.filter(geom_point__within=poly)
        self.assertEqual(len(features), 2)

    def test_point_within_mpolygon_double(self):
        create_points()
        poly1, poly2 = create_polygons()
        mpoly = geos.MultiPolygon(poly1, poly2)
        features = Feature.objects.filter(geom_point__within=mpoly)
        self.assertEqual(len(features), 2)

    def test_is_treated(self):
        p = geos.Point((-12018143.159491, 3711914.6000511))
        feature = Feature.objects.create(geom_point=p)
        self.user.map.featurestatus_set.create(treated=True,
                                               feature=feature,
                                               user_map=self.user_map)
        self.assertTrue((feature.is_treated(self.user_map)))

    def test_get_states(self):
        state = Feature.objects.get_states()
        self.assertEqual(state, [u'Baja California'])

    def test_multicentroid(self):
        p1, p2 = geos.Point(10, 10), geos.Point(11, 11)
        f1 = Feature.objects.create(geom_point=p1)
        f2 = Feature.objects.create(geom_point=p2)
        mp = geos.MultiPoint([p1, p2])


class FeatureTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)
        features = Feature.objects.order_by('id').all()
        self.user_map.featurestatus_set.collect_features(self.user_map, features, 500)
        FeatureStatus.objects.clear_treatment_points(self.user.map)
        FeatureStatus.objects.clear_control_points(self.user.map)
        random_set = list(FeatureStatus.objects.order_by('pk').all().values_list('pk', flat=True))

        self.treatment_set = random_set[0:2]
        FeatureStatus.objects.filter(
            pk__in=self.treatment_set).update(treated=True)

        self.control_set = random_set[2:5]
        FeatureStatus.objects.filter(
            pk__in=self.control_set).update(controlled=True)

    def test_attribute_values_should_return_list_when_empty(self):
        self.assertEquals(AttributeValue.objects.attribute_values(None, None), [[]])
        self.assertEquals(AttributeValue.objects.attribute_values([], []), [[]])

    def test_get_treated_returns_features(self):
        features = Feature.objects.get_treated(self.user_map.id)
        feature_ids = [feature.id for feature in features]
        # true_features = Feature.objects.filter(feature_status__id__in=self.treatment_set)
        self.assertEquals(feature_ids, self.treatment_set)

    def test_get_treated_handles_null_return_as_empty_queryset(self):
        features = Feature.objects.get_treated(51135315)
        self.assertFalse(features.exists())

    def test_get_controlled_returns_features(self):
        features = Feature.objects.get_controlled(self.user_map.id)
        feature_ids = [feature.id for feature in features]
        # true_features = Feature.objects.filter(feature_status__id__in=self.control_set)
        self.assertEquals(feature_ids, self.control_set)

    def test_get_controlled_handles_null_return_as_empty_queryset(self):
        features = Feature.objects.get_controlled(5435454)
        self.assertFalse(features.exists())

    def test_get_forest_cover_returns_correct_forest_covers(self):
        feature_ids = Feature.objects.values_list('id', flat=True).order_by('id')
        self.assertItemsEqual(Feature.objects.get_forest_cover(feature_ids),
                              [(16, 22), (17, 2), (18, 17), (19, 64), (20, 21)])


class FeatureStatusTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)

    def load_data(self):
        #Pay attention, using this method increments the primary keys
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)
        features = Feature.objects.order_by('id').all()
        self.user_map.featurestatus_set.collect_features(self.user_map, features, 500)
        FeatureStatus.objects.clear_treatment_points(self.user.map)
        FeatureStatus.objects.clear_control_points(self.user.map)
        random_set = list(FeatureStatus.objects.order_by('pk').all().values_list('pk', flat=True))
        treatment_set = random_set[0:2]
        FeatureStatus.objects.filter(pk__in=treatment_set).update(treated=True)
        control_set = random_set[2:5]
        FeatureStatus.objects.filter(pk__in=control_set).update(controlled=True)

    def test_set_control_points_by_radius(self):
        self.load_data()
        FeatureStatus.objects.set_control_points_by_radius(self.user_map, 10, 20)

    def test_select_treatment_points(self):
        p1, p2, f1, f2 = create_points()
        poly1, poly2 = create_polygons()
        mpoly = geos.MultiPolygon(poly1, poly2)
        self.user_map.featurestatus_set.collect_features(self.user_map, [f1, f2], 500)
        FeatureStatus.objects.set_treatment_points(self.user.map.id, mpoly)
        feature = self.user.map.featurestatus_set.filter(treated=True)
        self.assertEqual(len(feature), 2)

    def test_select_protected_areas(self):
        FeatureStatus.objects.select_protected_areas(self.user_map)

    def test_set_forest_cover_filter_runs(self):
        self.load_data()
        FeatureStatus.objects.set_forest_cover_filter(self.user_map, 30, 70)
        test_values = list(FeatureStatus.objects.filter(forest_filter=True).all())
        self.assertEqual(test_values[0].feature_id, 16)

    def test_set_control_points_remove_spillovers(self):
        self.load_data()
        FeatureStatus.objects.set_control_points_remove_spillovers(self.user_map, 10)


class AttributeValueTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)
        features = Feature.objects.order_by('id').all()
        self.user_map.featurestatus_set.collect_features(self.user_map, features, 500)
        FeatureStatus.objects.clear_treatment_points(self.user.map)
        FeatureStatus.objects.clear_control_points(self.user.map)
        random_set = list(FeatureStatus.objects.order_by('pk').all().values_list('pk', flat=True))
        treatment_set = random_set[0:2]
        FeatureStatus.objects.filter(pk__in=treatment_set).update(treated=True)
        control_set = random_set[2:5]
        FeatureStatus.objects.filter(pk__in=control_set).update(controlled=True)

    def test_attribute_values_runs(self):
        map_id = self.user.map.id
        covariates = ['forest_los', 'forest_cov']  # Must be a list
        outcome = ['forest_los']

        treated_features = Feature.objects.filter(
            featurestatus__user_map=map_id,
            featurestatus__treated=True)

        controlled_features = Feature.objects.filter(
            featurestatus__user_map=map_id,
            featurestatus__controlled=True)

        features = list(chain(treated_features, controlled_features))
        feature_ids = [feature.id for feature in features]
        test = AttributeValue.objects.attribute_values(outcome, feature_ids)[:]

    def test_attribute_values_should_return_feature_in_same_order(self):
        assert False, 'Not implemented'
