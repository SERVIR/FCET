# from django.db import models
# from django.utils import timezone #Do not use datetime due to locale
# from django.contrib.auth.models import User
# from django.contrib.gis.gdal import DataSource
# from django.contrib.gis.geos import GEOSGeometry
#
# class Upload(models.Model):
#     upload_id = models.BigIntegerField(null=True)
#     user = models.ForeignKey(User, null=True)
#     # hold importer state or internal state (STATE_)
#     #state = models.CharField(max_length=16)
#     date = models.DateTimeField('date', default=timezone.now)
#     #Maybe I won't have a layer model to connect to
#     #layer = models.ForeignKey(Layer, null=True)
#     upload_dir = models.CharField(max_length=100, null=True)
#     name = models.CharField(max_length=64, null=True)
#     #How does complete interact with sessions?
#     geom_type = models.CharField(max_length=50)
#     encoding = models.CharField(max_length=20)
#     #complete  = models.BooleanField(default=False)
#     #session  = models.TextField(null=True)
#
#     def upload_features(self, file_location, slice_stop=None):
#         '''
#         Loads layer features from uploaded file with matching attributes
#
#         Attributes:
#             file_location:Where the downloaded file was stored
#             slice_stop: The number of features to load in.
#         '''
#         ds = DataSource(file_location)
#         layer = ds[0]
#         layer_slice = slice(slice_stop)
#         data_features = layer[layer_slice]
#         attributes = []
#         for field in layer.fields:
#             # attribute = self.attribute_set.create(name=field)
#             attribute = Attribute(name=field, upload=self)
#             attributes.append(attribute)
#         Attribute.objects.bulk_create(attributes)
#
#         attribute_values = []
#         features = []
#         for data_feature in data_features:
#             #Create django feature
#             feature = Feature(geom_point=GEOSGeometry(data_feature.geom.wkt), shapefile=self)
#             features.append(feature)
#
#             #Create django attributes
#             for attribute in attributes:
#                 self.attribute_set.add(attribute)
#                 attribute_value = AttributeValue(
#                         attribute=attribute,
#                         value=unicode(feature.get(attribute.name)).encode('utf-8'),
#                         feature=feature)
#                 attribute_values.append(attribute_value)
#         Feature.objects.bulk_create(features)
#         AttributeValue.objects.bulk_create(attribute_values)
#
# #Create upload file
# class UploadFile(models.Model):
#     upload = models.ForeignKey(Upload, null=True, blank=True)
#     upload_file = models.FileField(upload_to="uploads")
#     slug = models.SlugField(max_length=50, blank=True)
#
#     def __unicode__(self):
#             return self.slug
#
#     def save(self, *args, **kwargs):
#         self.slug = self.upload_file.name
#         super(UploadFile, self).save(*args, **kwargs)
#
#     def delete(self, *args, **kwargs):
#         self.slug = self.upload_file.name
#         super(UploadFile, self).delete(*args, **kwargs)
