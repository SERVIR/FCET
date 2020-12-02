from django.test import TestCase
from django.contrib.auth.models import User
# from upload.models import Upload
import upload.views
from layers.models import Feature, Attribute
from map.models import Map
from django.test.client import RequestFactory


class UploadTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.map = Map.objects.create(user=self.user)
        self.factory = RequestFactory()

    def test_upload_5features_should_load_5_features(self):
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)
        self.assertEqual(len(Feature.objects.all()), 5)

    def test_upload_5features_should_load_attributes(self):
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)
        self.assertIsNotNone(Attribute.objects.first())
