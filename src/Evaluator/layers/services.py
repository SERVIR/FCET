# -*- coding: utf-8 -*-
"""
Each function represents a common task that a user can perform. Each function contains logic that manipulates either a django model or an adapter class that makes it
easier to change the database backend from django models, another ORM, or another database library.
These functions are called from the view files that handle networking, user authentication/identification, ...

The adapters are currently in this file, implemented as classes, but one could easily turn them into modules if this file
becomes so large as to warrant splitting up the code. Each adapter stems from a baseline AbstractFeatureStatusAdapter --
a correct implementation of each method in the abstract class should give a new functioning backend for the app.
For instance, if the PostgreSQL table it too slow and can't scale you may use Redis to store the statuses of each feature.
You would then need to code a redis adapter and the rest of the code should mostly work. You would also need to change
the SQL query in GeoServer used to generate layers. GeoServer is tightly coupled with PostgreSQL, but it's possible to
use a Foreign Data Wrapper to overcome this limitation.

At one point the schema for keeping track of the user's features was in first normal form with each feature as one row
in the database. This proved to be too slow and the flexibility of first normal form was not needed. We now store every
row as a user-set pair with an array of feature ids in each row.

When dealing with the status of features, we have to determine whether each feature on the screen is
selected, filtered, treated, controlled, or matched. This logic is tricky because we can't treat unselected feature and
we don't want features to be both treated and controlled. In other words, the sets have conditional dependencies -- we
even have to decide whether treated status can overwrite control status. Unfortunately, the logic for dealing with this
depends on the database back end and gets placed in the adapter classes. However we can test the correctness of the
logic in the functions. Rather than wasting runtime resources doing these tests, it's better just to have a
test suite (not yet made) to check the correctness of an adapter when it's plugged in.
"""

from .models import Feature, FeatureStatus, FastFeatureStatus, Attribute, AttributeValue
import logging
from gc import collect
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.measure import D
from abc import ABCMeta, abstractmethod
import random
import warnings

logger = logging.getLogger(__name__)


class AbstractFeatureStatusAdapter(object):
    @abstractmethod
    def get_treated(self, user_map):
        pass

    @abstractmethod
    def set_treated(self, user_map, treated):
        pass

    @abstractmethod
    def clear_treated(self, user_map):
        pass

    @abstractmethod
    def get_controlled(self, user_map):
        pass

    @abstractmethod
    def set_controlled(self, user_map, controlled):
        pass

    @abstractmethod
    def clear_controlled(self, user_map):
        pass

    @abstractmethod
    def delete_controlled(self, user_map, controlled):
        pass

    @abstractmethod
    def get_matched(self, user_map):
        pass

    @abstractmethod
    def set_matched(self, user_map, matches):
        pass

    @abstractmethod
    def clear_matched(self, user_map):
        pass

    @abstractmethod
    def get_forest_filter(self, user_map):
        pass

    @abstractmethod
    def set_forest_filter(self, user_map, features):
        pass

    @abstractmethod
    def clear_forest_filter(self, user_map):
        pass

    @abstractmethod
    def get_unmarked_studyarea_in_polygons(self, user_map, mpoly):
        pass

    @abstractmethod
    def collect_features(self, user_map, features, chunksize=1000):
        pass

    @abstractmethod
    def set_selected(self, user_map, features, chunksize=1000):
        pass

    @abstractmethod
    def add_selected(self, user_map, features):
        pass

    @abstractmethod
    def remove_selected(self, user_map, features):
        pass

    @abstractmethod
    def clear_selected(self, user_map):
        pass

    @abstractmethod
    def get_candidates(self, user_map):
        pass

    @abstractmethod
    def set_candidates(self, user_map, feature_ids):
        pass

    @abstractmethod
    def add_candidates(self, user_map, feature_ids):
        pass

    @abstractmethod
    def remove_candidates(self, user_map, feature_ids):
        pass

    @abstractmethod
    def clear_candidates(self, user_map):
        pass

    @abstractmethod
    def get_all(selfself, user_map):
        pass

class PostgresRelationalFSA(AbstractFeatureStatusAdapter):
    def get_treated(self, user_map):
        return list(
                FeatureStatus.objects
                    .filter(user_map=user_map, treated=True)
                    .values_list('feature_id', flat=True)
        )

    def set_treated(self, user_map, treated):
        (
            FeatureStatus.objects
                .filter(user_map=user_map, feature_id__in=treated, controlled=False)
                .update(treated=True)
        )

    def clear_treated(self, user_map):
        FeatureStatus.objects.filter(user_map=user_map).update(treated=False)

    def get_controlled(self, user_map):
        return list(
                FeatureStatus.objects
                    .filter(user_map=user_map, controlled=True)
                    .values_list('feature_id', flat=True)
        )

    def set_controlled(self, user_map, controlled):
        (
            FeatureStatus.objects
                .filter(user_map=user_map, feature_id__in=controlled, treated=False)
                .update(controlled=True)
        )

    def clear_controlled(self, user_map):
        FeatureStatus.objects.filter(user_map=user_map).update(controlled=False)

    def delete_controlled(self, user_map, controlled):
        FeatureStatus.objects.filter(user_map=user_map, feature_id__in=controlled).update(controlled=False)

    def get_matched(self, user_map):
        return list(
                FeatureStatus.objects
                    .filter(user_map=user_map, matched=True)
                    .values_list('feature_id', flat=True)
        )

    def set_matched(self, user_map, matches):
        points = FeatureStatus.objects.filter(feature_id__in=matches)
        treatment_set = points.filter(user_map=user_map)
        treatment_set = treatment_set.exclude(treated=True)
        treatment_set.update(matched=True)

    def clear_matched(self, user_map):
        FeatureStatus.objects.filter(user_map=user_map).update(matched=False)

    def set_forest_filter(self, user_map, features):
        FeatureStatus.objects.filter(user_map=user_map, feature_id__in=features).update(forest_filter=True)

    def clear_forest_filter(self, user_map):
        FeatureStatus.objects.filter(user_map=user_map).update(forest_filter=False)

    def get_unmarked_studyarea_in_polygons(self, user_map, mpoly):
        return list(
                FeatureStatus.objects
                    .filter(feature__geom_point__within=mpoly, user_map=user_map)
                    .exclude(controlled=True, treated=True)
                    .values_list('feature_id', flat=True)
        )

    def get_study_area(self, user_map):
        return list(
                FeatureStatus.objects
                    .filter(user_map=user_map)
                    .values_list('feature_id', flat=True)
        )

    def collect_features(self, user_map, features, chunksize=1000):
        """Attaches all uploaded features to user map"""
        logger.debug("Collecting Features")
        chunk = chunksize
        feature_chunk = list(features[:chunk])
        while feature_chunk:
            logger.debug("Stepping into Feature chunk")
            feature_status_list = [FeatureStatus(user_map=user_map,
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


class PostgresFSA(AbstractFeatureStatusAdapter):
    def get_treated(self, user_map):
        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="TREATED")
        return ffs.feature_set

    def set_treated(self, user_map, new_treated):
        study_area = set(self.get_selected(user_map))
        controlled = set(self.get_controlled(user_map))
        matched = set(self.get_matched(user_map))
        treated = set(self.get_treated(user_map))
        forest_filtered = set(self.get_forest_filter(user_map))

        new_treated = list(study_area & (treated | set(new_treated)) - controlled - forest_filtered)
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="TREATED").update(feature_set=new_treated)

    def clear_treated(self, user_map):
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="TREATED").update(feature_set=[])

    def get_controlled(self, user_map):
        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="CONTROLLED")
        return ffs.feature_set

    def set_controlled(self, user_map, new_controlled):
        study_area = set(self.get_selected(user_map))
        controlled = set(self.get_controlled(user_map))
        matched = set(self.get_matched(user_map))
        treated = set(self.get_treated(user_map))
        forest_filtered = set(self.get_forest_filter(user_map))

        controlled = list(study_area & (controlled | set(new_controlled)) - treated - forest_filtered)
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CONTROLLED").update(feature_set=controlled)

    def clear_controlled(self, user_map):
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CONTROLLED").update(feature_set=[])

    def delete_controlled(self, user_map, controlled):
        new_controlled = list(set(self.get_controlled(user_map)) - set(controlled))
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CONTROLLED").update(
                feature_set=new_controlled)

    def get_matched(self, user_map):
        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="MATCHED")
        return ffs.feature_set

    def set_matched(self, user_map, matches):
        controlled = set(self.get_controlled(user_map))
        matched = set(self.get_matched(user_map))
        treated = set(self.get_treated(user_map))
        forest_filtered = set(self.get_forest_filter(user_map))
        assert len(set(matches) & forest_filtered) == 0, "Some matched points are in the group of filtered points " \
                                                         "that have been filtered out due to forest cover"
        matched = list(set(matches))
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="MATCHED").update(feature_set=matched)

    def clear_matched(self, user_map):
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="MATCHED").update(feature_set=[])

    def get_forest_filter(self, user_map):
        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="FORESTFILTER")
        return ffs.feature_set

    def set_forest_filter(self, user_map, features):
        forest_filtered = self.get_forest_filter(user_map)
        forest_filtered = list(set(features))
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="FORESTFILTER").update(
                feature_set=forest_filtered)

    def clear_forest_filter(self, user_map):
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="FORESTFILTER").update(feature_set=[])

#    def get_points_in_polygons(self, multi_polygons):
#        points = set()
#        for multi_polygon in multi_polygons:
#            points.update(
#                list(
#                    Feature.objects
#                        .filter(geom_point__within=multi_polygon)
#                    )
#            )
#        return [point.id for point in points]
    def get_points_in_polygons(self, mpoly):
        return [f.id
                for f in Feature.objects.raw(
                    '''SELECT "layers_feature"."id"
                       FROM "layers_feature", (
                          SELECT (ST_DUMP(ST_GeomFromWKB(%s, 4326))).geom AS geometry) as selection
                          WHERE ST_Contains(selection.geometry, geom_point)''',
                    params=[mpoly.wkb])]
        return [point.id for point in points]

    def get_unmarked_studyarea_in_polygons(self, user_map, mpoly):
        # This has had some quick changes made recently and should be inspected
        # This now retrieves all points within a polygon
        # There is some room left open for foul play if people select very large polygons ... see if this can be fixed without breaking performance

        #unmarked_studyarea = FastFeatureStatus.objects.get(user_map=user_map, set_type="SELECTED").feature_set
        # We use a raw query for performance reasons, standard django does allow Postgresql to build an efficient query plan
        # Turns out if you use a single multipolygon, PostGIS will use a single bbox and won't make good use of the geometry index
        # Instead we make a table in a subquery of several small polygons a cartesian join between this table and the feature table make good use of our index
        return [f.id
                for f in Feature.objects.raw(
                    '''SELECT "layers_feature"."id"
                       FROM "layers_feature", (
                          SELECT (ST_DUMP(ST_GeomFromWKB(%s, 4326))).geom AS geometry) as selection
                          WHERE ST_Contains(selection.geometry, geom_point)''',
                    params=[mpoly.wkb])]

    def collect_features(self, user_map, features, chunksize=1000):
        feature_ids = [feature.id for feature in features]

        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="SELECTED")
        selected = list(set(feature_ids))
        ffs.feature_set = selected

    def get_selected(self, user_map):
        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="SELECTED")
        return ffs.feature_set

    def set_selected(self, user_map, feature_ids):
        #ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="SELECTED")
        selected = self.get_selected(user_map)
        selected = list(set(feature_ids))
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="SELECTED").update(feature_set=selected)

    def add_selected(self, user_map, feature_ids):
        selected = set(self.get_selected(user_map))
        new_selected = set(feature_ids)
        new_selected = list(selected | new_selected)

        FastFeatureStatus.objects.filter(user_map=user_map, set_type="SELECTED").update(feature_set=new_selected)

    def remove_selected(self, user_map, feature_ids):
        selected = set(self.get_selected(user_map))
        unselect = set(feature_ids)
        new_selected = list(selected - unselect)

        FastFeatureStatus.objects.filter(user_map=user_map, set_type="SELECTED").update(feature_set=new_selected)

    def clear_selected(self, user_map):
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="SELECTED").update(feature_set=[])

    def get_candidates(self, user_map):
        ffs, created = FastFeatureStatus.objects.get_or_create(user_map=user_map, set_type="CANDIDATES")
        return ffs.feature_set

    def set_candidates(self, user_map, feature_ids):
        candidates = list(set(feature_ids))
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CANDIDATES").update(feature_set=candidates)

    def add_candidates(self, user_map, feature_ids):
        candidates = set(self.get_candidates(user_map))
        new_candidates = set(feature_ids)
        new_candidates = list(candidates | new_candidates)

        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CANDIDATES").update(feature_set=new_candidates)

    def remove_candidates(self, user_map, feature_ids):
        candidates = set(self.get_candidates(user_map))
        candidates_to_remove = set(feature_ids)
        new_candidates = list(candidates - candidates_to_remove)

        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CANDIDATES").update(feature_set=new_candidates)

    def clear_candidates(self, user_map):
        FastFeatureStatus.objects.filter(user_map=user_map, set_type="CANDIDATES").update(feature_set=[])

    def get_all(self, user_map):
        """
        Return all points that appear on the user map
        """
        all_features_on_map = set(self.get_selected(user_map)) | set(self.get_treated(user_map)) | \
                              set(self.get_controlled(user_map)) | set(self.get_matched(user_map))
        return all_features_on_map

# fs_manager = PostgresRelationalFSA()
fs_manager = PostgresFSA()


def get_points_by_polygons(multi_polygons):
    return fs_manager.get_points_in_polygons(multi_polygons)

def set_treatment_points(user_map, mpoly):
    """Set features belonging to user within mpoly to be treated"""
    treatment_set = fs_manager.get_unmarked_studyarea_in_polygons(user_map, mpoly)
    fs_manager.set_treated(user_map, treatment_set)
    warnings.warn("set_treatment_points will change to accept points only")

def set_treatment_points_correct(user_map, treatment_set):
    fs_manager.set_treated(user_map, treatment_set)

def get_treatment_points(user_map):
    return fs_manager.get_treated(user_map)


def select_protected_areas(user_map):
    attribute_id = Attribute.objects.filter(name='protctd')
    feature_ids = fs_manager.get_selected(user_map=user_map)
    feature_ids = list(
            AttributeValue.objects
                .filter(attribute_id__in=attribute_id, feature_id__in=feature_ids, value='1.0')
                .values_list('feature_id', flat=True)
    )

    fs_manager.set_treated(user_map, feature_ids)


def set_control_points(user_map, mpoly):
    """Set features belonging to user within mpoly to be controlled"""
    control_set = fs_manager.get_unmarked_studyarea_in_polygons(user_map, mpoly)
    fs_manager.set_controlled(user_map, control_set)


def get_control_points(user_map):
    return fs_manager.get_controlled(user_map)


def get_selected_points(user_map):
    return fs_manager.get_selected(user_map)


def clear_control_points(user_map):
    """Set features belonging to user to not be in the control group"""
    fs_manager.clear_controlled(user_map)


def set_control_points_by_radius(user_map, lower, upper):
    """
    Set feature belonging to a user within a min and max radius of
    the selected treatment group
    """
    clear_control_points(user_map)
    treated = fs_manager.get_treated(user_map)
    selected = fs_manager.get_selected(user_map)
    point_rows = list(
            Feature.objects
                .filter(pk__in=treated)
                .values_list('geom_point', flat=True)
    )

    mpoints = MultiPoint(point_rows)
    bounded = list(
            Feature.objects
                .filter(pk__in=selected)
                .filter(geom_point__distance_lte=(mpoints, D(km=upper)),
                        geom_point__distance_gte=(mpoints, D(km=lower)))
                .values_list('id', flat=True)
    )
    fs_manager.set_controlled(user_map, bounded)


def set_control_points_remove_spillovers(user_map, upper):
    """
    Set control features for user by removing points which are near treated points and
    fall within a specified radius

    :param user_map: Map instance associated with the logged in user
    :param upper: Number to set radius that bounds the spillover region
    :return: None, do database I/O
    """
    treated = fs_manager.get_treated(user_map)
    point_rows = list(
            Feature.objects
                .filter(pk__in=treated)
                .values_list('geom_point', flat=True)
    )

    METER_TO_ARC = 111195.0 # Divide meters by this value to get degree arcs in SRID 4326
    mpoints = MultiPoint(point_rows)

    controlled = fs_manager.get_controlled(user_map)
    bounded = list(
            Feature.objects
                .filter(pk__in=controlled, geom_point__distance_lte=(mpoints, D(km=upper)))
                .values_list('id', flat=True)
    )

    fs_manager.delete_controlled(user_map, bounded)

def set_control_points_by_study_area(user_map):
    study_area = fs_manager.get_selected(user_map=user_map)
    fs_manager.set_controlled(user_map, study_area)

#def collect_features(map, features, chunksize=1000):
#    fs_manager.collect_features(user_map=map, features=features, chunksize=1000)

def collect_feature_ids(user_map, features, chunksize=1000):
    fs_manager.clear_treated(user_map=user_map)
    fs_manager.clear_controlled(user_map=user_map)
    fs_manager.clear_matched(user_map=user_map)
    fs_manager.add_candidates(user_map=user_map, feature_ids=features)
    _reduce_sample_size(user_map, fs_manager.get_candidates(user_map=user_map))
    new_features = _reduce_sample_size(user_map, fs_manager.get_candidates(user_map=user_map))
    fs_manager.set_selected(user_map=user_map, feature_ids=new_features)

def unselect_features(user_map, features):
    fs_manager.clear_treated(user_map=user_map)
    fs_manager.clear_controlled(user_map=user_map)
    fs_manager.clear_matched(user_map=user_map)
    fs_manager.remove_candidates(user_map=user_map, feature_ids=features)
    fs_manager.remove_selected(user_map=user_map, feature_ids=features)

def set_matched_points(user_map, matches):
    """Set features belonging to user to be matched"""
    fs_manager.set_matched(user_map=user_map, matches=matches)


def clear_treatment_points(user_map):
    """Set features belonging to user to not be treated"""
    fs_manager.clear_treated(user_map=user_map)


def clear_matched_points(user_map):
    """Set features belonging to user to not be matched"""
    fs_manager.clear_matched(user_map=user_map)


def clear_selected_points(user_map):
    fs_manager.clear_candidates(user_map=user_map)
    fs_manager.clear_selected(user_map=user_map)


def set_forest_cover_filter(user_map, lower_bound, upper_bound):
    """
    Update forest_filter column in feature status to flag if a point has the correct forest cover for use in analysis.
    A filtered point is one that does not show up on the map. Filtered points must be a subset of selected points.

    :param user_map: Map instance associated with the logged in user
    :param lower_bound: The lower bound of forest cover to keep
    :param upper_bound: The upper bound of forest cover to keep
    :return: None
    """

    # Get user's points
    feature_ids = fs_manager.get_selected(user_map=user_map)
    attribute_ids = [a.id for a in Attribute.objects.filter(name='frst_cv')]

    feature_forest_cover = dict(AttributeValue.objects.filter(
            feature_id__in=feature_ids,
            attribute_id__in=attribute_ids).values_list('feature_id', 'value'))

    feature_forest_cover = [(id, float(feature_forest_cover[id])) for id in feature_ids]
    assert max(forest_cover for (fid, forest_cover) in feature_forest_cover) != 0.0, 'All forest cover is 0, looks like a data error'

    # Find points with that are NOT in the filter range
    features_in_range = [feature_id
                         for (feature_id, forest_cover) in feature_forest_cover
                         if
                         # (float(lower_bound) <= float(forest_cover)) and (float(forest_cover) <= float(upper_bound))]
                         (float(forest_cover) <= float(lower_bound)) or (float(upper_bound) <= float(forest_cover))]

    clear_forest_cover_filter(user_map=user_map)  # This is false so we can return to a state where no points are shown
    fs_manager.set_forest_filter(user_map=user_map, features=features_in_range)
    fs_manager.clear_treated(user_map)
    fs_manager.clear_controlled(user_map)
    fs_manager.clear_matched(user_map)


def clear_forest_cover_filter(user_map):
    """
    Update forest_filter column to False to reset the forest filter to True and let all all points be visible

    :param user_map: Map id associated with the logged in user
    :return: None
    """
    fs_manager.clear_forest_filter(user_map=user_map)

def get_points_in_polygons(multipolygons):
    return fs_manager.get_points_in_polygons(multipolygons)

def _reduce_sample_size(user_map, candidates):
    TARGET_SIZE = 50000
    candidate_length = len(candidates)
    if candidate_length > TARGET_SIZE:
        features = random.sample(candidates, TARGET_SIZE)
    else:
        features = candidates

    return features

APPROVED_COVARIATES = {
                   #'pointid': '',
                   'latitud': 'Latitude',
                   'longitd': 'Longitude',
                   #'state': '',
                   #'state_num': '',
                   'frst_cv': 'Forest Cover',
                   #'frst_ls': 'Forest Loss',
                   'slope': 'Slope',
                   'aspect': 'Aspect',
                   'dem': 'Elevation',
                   'ttim_mn': 'Travel Time',
                   'pdensty': 'Population Density',
                   'ds_t_ct': 'Distance to City',
                   'rain': 'Rain',
                   'temp': 'Temperature',
                   #'protctd': '',
                   #'grid_code': '',
                   'oppcost': 'Opportunity Cost',
                   'tenure_typ': 'Tenure Type',
                   #'im_2010': '',
                   'marginaliz': 'Marginalization',
                   'dstclrn': 'Distance to Clearing'
                   }

def legible_covariate_names(name):
    rename_dict = APPROVED_COVARIATES
    return rename_dict[name]

