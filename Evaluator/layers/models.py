from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.measure import D
# from upload.models import Upload
from map.models import Map
from django.contrib.gis.geos import MultiPoint
from gc import collect
from os import environ
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone #Do not use datetime due to locale
from django.contrib.auth.models import User
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.core.cache import cache

environ['MPLCONFIGDIR'] = '/tmp/'
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Upload(models.Model):
    upload_id = models.BigIntegerField(null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    # hold importer state or internal state (STATE_)
    #state = models.CharField(max_length=16)
    date = models.DateTimeField('date', default=timezone.now)
    #layer = models.ForeignKey(Layer, null=True)
    upload_dir = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=64, null=True)
    #How does complete interact with sessions?
    geom_type = models.CharField(max_length=50)
    encoding = models.CharField(max_length=20)
    #complete  = models.BooleanField(default=False)
    #session  = models.TextField(null=True)

    def upload_features(self, file_location, slice_stop=None):
        '''
        Loads layer features from uploaded file with matching attributes

        Attributes:
            file_location:Where the downloaded file was stored
            slice_stop: The number of features to load in.
        '''
        import logging
        import sys
        from django.db import connection
        import itertools


        ds = DataSource(file_location)
        layer = ds[0]
        #assert False, dir(layer)
        #geoms = layer.get_geoms()
        #for geom in geoms:
        #    geom.transform('4326')

        if slice_stop == None:
            slice_stop = len(layer) - 1

        attributes = []
        for field in layer.fields:
            attribute = Attribute(name=field, shapefile=self)
            attributes.append(attribute)
       # Attribute.objects.bulk_create(attributes)
        for attribute in attributes:
            self.attribute_set.add(attribute)

        size = 25000
        chunks = (layer[i:i+size] for i in range(0, slice_stop, size))
        for bulk_ref, data_features in enumerate(chunks):
            collect()
            print("batch {} of {}".format(int(bulk_ref), slice_stop/size))
            print("data features take: %s bytes" % sys.getsizeof(data_features))

            print("collecting features")
            numbered_features = list(enumerate(data_features))
            #features = [Feature(geom_point=GEOSGeometry(df.geom.wkt), shapefile=self, row_id=id, bulk_ref=bulk_ref)
            #            for (id, df)
            #            in numbered_features]
            features = [Feature(geom_point=GEOSGeometry(df.geom.transform('4326', clone=True).wkt), shapefile=self, row_id=id, bulk_ref=bulk_ref)
                        for (id, df)
                        in numbered_features]
            #for id, df in numbered_features:
            #    print GEOSGeometry(df.transform('4326'))

            print("features take: %s bytes" % sys.getsizeof(features))
            print("feature bulk insert")
            Feature.objects.bulk_create(features)
            collect()
            print("Finished feature bulk insert")

            print("Getting feature ids")
            feature_pairs = zip(list(Feature.objects
                                     .filter(shapefile=self,
                                             row_id__in=[id for id, _ in numbered_features],
                                             bulk_ref=bulk_ref)
                                     .order_by('row_id')),
                                data_features)
            print("feature pairs take: %s bytes" % sys.getsizeof(feature_pairs))

            print("Generating feature attributes")
            cursor = connection.cursor()
            attribute_values = []
            for feature_pair, attribute in itertools.product(feature_pairs, attributes):
                #Create django attributes
                feature, data_feature = feature_pair
                attribute_value = (feature.id, attribute.id, unicode(data_feature.get(attribute.name)).encode('utf-8'))
                attribute_values.append(attribute_value)
            sql = 'INSERT INTO "layers_attributevalue" ("feature_id", "attribute_id", "value") VALUES ' + str(attribute_values).strip('[]')
            print("attribute values take: %s bytes" % sys.getsizeof(attribute_values))
            del attribute_values
            print("SQL takes: %s bytes" % sys.getsizeof(sql))
            print("Attribute value bulk insert")
            cursor.execute(sql)
            print("Finished attribute value bulk insert")
        ds = None

#Create upload file
class UploadFile(models.Model):
    upload = models.ForeignKey(Upload, null=True, blank=True, on_delete=models.CASCADE)
    upload_file = models.FileField(upload_to="uploads")
    slug = models.SlugField(max_length=50, blank=True)

    def __unicode__(self):
            return self.slug

    def save(self, *args, **kwargs):
        self.slug = self.upload_file.name
        super(UploadFile, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.slug = self.upload_file.name
        super(UploadFile, self).delete(*args, **kwargs)

class FeatureManager(geomodels.Manager):
    def get_states(self):
        attribute_id = Attribute.objects.get(name='state').id
        states = list(AttributeValue.objects.filter(
                attribute_id=attribute_id).distinct().values_list('value', flat=True))
        return states

    def get_treated(self, map_id):
        """
        Get treated features that match the map_id and 
        hence correspond to a user
        """
        treated_features = Feature.objects.filter(
                featurestatus__user_map=map_id,
                featurestatus__treated=True)
        return treated_features

    def get_controlled(self, map_id):
        """
        Get controlled features that match the map_id and 
        hence correspond to a user
        """
        controlled_features = Feature.objects.filter(
                featurestatus__user_map=map_id,
                featurestatus__controlled=True)
        return controlled_features

    def get_forest_cover(self, feature_ids):
        """
        Retrieve array of forest cover values for a given set of features

        :param map_id: Id of map belonging to user
        :param feature_ids: List of features
        :return: Array of forest cover values
        """
        forest_cover_attribute_id = Attribute.objects.get_by_name(['frst_cv']).values_list('id').get()
        forest_cover_values = dict(AttributeValue.objects.filter(
                feature_id__in=feature_ids,
                attribute_id=forest_cover_attribute_id).values_list('feature_id', 'value'))
        return [(id, float(forest_cover_values[id])) for id in feature_ids]


class Feature(geomodels.Model):
    """
    Stores a single layer feature, related to :model:`upload.Upload`
    """
    SRID = 4326

    shapefile = models.ForeignKey(Upload, null=True, on_delete=models.CASCADE)
    row_id = models.IntegerField()
    bulk_ref = models.IntegerField()
    user_maps = models.ManyToManyField(Map, through='FeatureStatus')
    geom_point = geomodels.PointField(srid=SRID,blank=True, null=True)
    geom_multipoint = geomodels.MultiPointField(srid=SRID,blank=True, null=True)
    geom_multilinestring = geomodels.MultiLineStringField(srid=SRID,blank=True, null=True)
    geom_multipolygon = geomodels.MultiPolygonField(srid=SRID,blank=True, null=True)
    geom_geometrycollection = geomodels.GeometryCollectionField(srid=SRID,blank=True, null=True)
    objects = FeatureManager()

    def add_fields(self, feature, attributes):
        """Adds attributes to feature from uploaded file feature"""
        attribute_values = []
        for attribute in attributes:
            self.attribute_set.add(attribute)
            attribute_value = AttributeValue(
                    attribute=attribute,
                    value=unicode(feature.get(attribute.name)).encode('utf-8'),
                    feature=self)
            attribute_values.append(attribute_value)
        attribute.attributevalue_set.bulk_create(attribute_values)

    def is_treated(self, user_map):
        return [f.treated for f
                in self.featurestatus_set.filter(user_map=user_map)]


class FeatureStatusManager(models.Manager):
    """Helper class for FeatureStatus"""

    def set_treatment_points(self, user_map, mpoly):
        """Set features belonging to user within mpoly to be treated"""
        points = FeatureStatus.objects.filter(
                feature__geom_point__within=mpoly)
        treatment_set = points.filter(user_map=user_map)
        treatment_set = treatment_set.exclude(controlled=True)
        treatment_set.update(treated=True)

    def select_protected_areas(self, user_map):
        attribute_id = Attribute.objects.filter(name='protected').first()
        feature_ids = list(
                AttributeValue.objects.filter(
                        attribute_id=attribute_id,
                        value='1.0').values_list('feature_id', flat=True))

        points = FeatureStatus.objects.filter(
                feature__in=feature_ids).filter(user_map=user_map)
        points.update(treated=True)

    def set_control_points(self, user_map, mpoly):
        """Set features belonging to user within mpoly to be controlled"""
        points = FeatureStatus.objects.filter(
                feature__geom_point__within=mpoly)
        treatment_set = points.filter(user_map=user_map)
        treatment_set = treatment_set.exclude(treated=True)
        treatment_set.update(controlled=True)

    def set_control_points_by_radius(self, user_map, lower, upper):
        """
        Set feature belonging to a user within a min and max radius of
        the selected treatment group
        """
        self.clear_control_points(user_map)
        point_rows = list(Feature.objects.filter(
                featurestatus__treated=True,
                user_maps=user_map.id).values_list('geom_point', flat=True))

        mpoints = MultiPoint(point_rows)
        bounded = FeatureStatus.objects.filter(
                feature__geom_point__distance_lte=(mpoints, D(km=upper)),
                feature__geom_point__distance_gte=(mpoints, D(km=lower))
        )

        new_control_points = bounded.filter(treated=False)
        new_control_points.update(controlled=True)

    def set_control_points_remove_spillovers(self, user_map, upper):
        """
        Set control features for user by removing points which are near treated points and
        fall within a specified radius

        :param user_map: Map instance
        :param upper: Number to set radius that bounds the spillover region
        :return: None, do database I/O
        """

        point_rows = list(Feature.objects.filter(
                featurestatus__treated=True,
                user_maps=user_map.id).values_list('geom_point', flat=True))

        mpoints = MultiPoint(point_rows)
        bounded = FeatureStatus.objects.filter(
                controlled=True,
                feature__geom_point__distance_lte=(mpoints, D(km=upper)))

        new_control_points = bounded.filter(treated=False)
        new_control_points.update(controlled=False)

    def set_control_points_by_study_area(self, user_map):
        points = FeatureStatus.objects.filter(user_map=user_map)
        control_set = points.exclude(treated=True)
        control_set.update(controlled=True)

    def collect_features(self, map, features, chunksize=1000):
        logger.debug("Collecting Features")
        """Attaches all uploaded features to user map"""
        chunk = chunksize
        feature_chunk = list(features[:chunk])
        while feature_chunk:
            logger.debug("Stepping into Feature chunk")
            feature_status_list = [FeatureStatus(user_map=map,
                                                 feature=feature,
                                                 treated=False,
                                                 controlled=False)
                                   for feature
                                   in feature_chunk]

            logger.debug("FeatureStatus bulkwrite")
            FeatureStatus.objects.bulk_create(feature_status_list)
            logger.debug("FeatureStatus bulkwrite complete")
            feature_chunk = list(features[chunk:chunk + chunksize])
            chunk += chunksize
            collect()

    def set_matched_points(self, user_map, matches):
        """Set features belonging to user within mpoly to be matched"""
        # what data structure should matches be?
        # That will determine the filter query
        points = FeatureStatus.objects.filter(feature_id__in=matches)
        treatment_set = points.filter(user_map=user_map)
        treatment_set = treatment_set.exclude(treated=True)
        treatment_set.update(matched=True)

    def clear_treatment_points(self, user_map):
        """Set features belonging to user to not be treated"""
        points = FeatureStatus.objects.filter(user_map=user_map)
        points.update(treated=False)

    def clear_control_points(self, user_map):
        """Set features belonging to user to not be controlled"""
        points = FeatureStatus.objects.filter(user_map=user_map)
        points.update(controlled=False)

    def clear_matched_points(self, user_map):
        """Set features belonging to user to not be matched"""
        points = FeatureStatus.objects.filter(user_map=user_map)
        points.update(matched=False)

    def set_forest_cover_filter(self, user_map, lower_bound, upper_bound):
        """
        Update forest_filter column in feature status to flag
        if a point has the correct forest cover for use in analysis

        :param user_map: Map id associated with the logged in user
        :param lower_bound: The lower bound of forest cover to keep
        :param upper_bound: The upper bound of forest cover to keep
        :return: None
        """

        # Get user's points
        feature_ids = FeatureStatus.objects.filter(user_map=user_map).values_list('feature_id', flat=True)

        feature_forest_cover = Feature.objects.get_forest_cover(feature_ids)

        # Find points with correct level of forest_cover
        features_in_range = [feature_id
                             for (feature_id, forest_cover) in feature_forest_cover
                             if
                             (float(lower_bound) < float(forest_cover)) and (float(forest_cover) < float(upper_bound))]

        FeatureStatus.objects.all().update(
                forest_filter=False)  # This is false so we can return to a state where no points are shown
        FeatureStatus.objects.filter(feature_id__in=features_in_range).update(forest_filter=True)

    def clear_forest_cover_filter(self, user_map):
        """
        Update forest_filter column to False to reset the forest filter to True and let all all points be visible

        :param user_map: Map id associated with the logged in user
        :return: None. Do I/O
        """

        FeatureStatus.objects.all().update(forest_filter=True)


class FeatureStatus(models.Model):
    """
    Extends the feature model to have treated and controlled attributes
    without creating a one to one relationship between feature and status
    """
    user_map = models.ForeignKey(Map, null=True, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, null=True, on_delete=models.CASCADE)
    treated = models.BooleanField(default=False)
    controlled = models.BooleanField(default=False)
    matched = models.BooleanField(default=False)
    forest_filter = models.BooleanField(default=True)
    objects = FeatureStatusManager()

    class Meta:
        unique_together = ('user_map', 'feature')

class FastFeatureStatus(models.Model):
    """
    Extends the feature model to have treated and controlled attributes
    without creating a one to one relationship between feature and status
    """
    user_map = models.ForeignKey(Map, null=True, on_delete=models.CASCADE)
    set_type = models.CharField(choices=(
        ('SELECTED', 'SELECTED'),
        ('TREATED', 'TREATED'),
        ('CONTROLLED', 'CONTROLLED'),
        ('MATCHED', 'MATCHED'),
        ('FORESTFILTER', 'FORESTFILTER'),
        ('ERROR', 'ERROR'),
    ), default='ERROR', max_length=12)
    feature_set = ArrayField(models.IntegerField(), default=list)

    class Meta:
        unique_together = ('user_map', 'set_type')

class AttributeManager(models.Manager):
    def get_by_name(self, names):
        """
        Retrieves attributes by name
        """
        try:
            iter(names)
        except TypeError:
            raise ValueError('Iterable expected')

        return Attribute.objects.filter(name__in=names)


class Attribute(models.Model):
    shapefile = models.ForeignKey(Upload, null=True, on_delete=models.CASCADE)
    user_map = models.ForeignKey(Map, null=True, on_delete=models.CASCADE)
    feature = models.ManyToManyField(Feature)
    name = models.CharField(max_length=255)  # Don't forget to the variable length similarly
    objects = AttributeManager()
    # type = models.IntegerField()
    # width = models.IntegerField()
    # precision = models.IntegerField()

class AttributeValueManager(models.Manager):
    def attribute_values(self, attribute_ids, feature_ids):
        """
        Retrieve attribute values for every attribute provided,
        for every feature id provided

        attribute_names: An ordered iterable of strings
        feature_ids: An ordered of feature IDs
        """
        logger.debug('Loading Attributes')
        from django.db import connection

        # Too much django overhead on this critical operation
        cursor = connection.cursor()
        fids = '('+','.join(str(x) for x in feature_ids)+')'
        aids = '('+','.join(str(x) for x in attribute_ids)+')'
        cursor.execute('SELECT feature_id, attribute_id, value FROM layers_attributevalue WHERE feature_id IN ' +
                                   fids + ' AND attribute_id IN '+aids+' ORDER BY feature_id, attribute_id')
        rows = cursor.fetchall()
        cursor.close()
        return rows

        #return AttributeValue.objects \
        #    .order_by('feature_id', 'attribute_id') \
        #    .filter(attribute_id__in=attribute_ids, feature_id__in=feature_ids) \
        #    .values('feature_id', 'attribute_id', 'value')

    def warm_cache(self, rate):
        from django.core.paginator import Paginator
        values = AttributeValue.objects \
            .order_by('feature_id', 'attribute_id') \
            .values('feature_id', 'attribute_id', 'value').all()

        paginator = Paginator(values, rate)
        for page in range(1, paginator.num_pages + 1):
            vals = paginator.page(page).object_list
            cache.set_many({str(val['attribute_id'])+'_'+str(val['feature_id']):val for val in vals}, None)
            print("done processing page %s of %s" % (page, paginator.num_pages))

    def test_cache(self, values):
        cache.get_many([str(val['attribute_id'])+'_'+str(val['feature_id']) for val in values])

class AttributeValue(models.Model):
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, blank=True, null=True)
    objects = AttributeValueManager()


