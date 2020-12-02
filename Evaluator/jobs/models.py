from django.db import models
from map.models import Map
from django.contrib.auth.models import User
from layers.models import Feature, AttributeValue
from psm import PropensityScoreMatching
from itertools import chain
from pickle import dump
from services import StatisticalMatchingAdapter
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class JobManager(models.Manager):
    def most_recent(self, user_map):
        '''Retrieve the most recent job run by a user'''
        assert isinstance(user_map, Map)
        return self.filter(usermap=user_map, current=True).order_by('-id')[0:1]

class Job(models.Model):
    '''
    Models a single matching procedure or report
    '''
    METHODS = (
        ('PSM', 'Propensity Score Matching'),
        ('MM', 'Mahalanobis Matching'),
    )
    ESTIMATORS = (('NN', 'Nearest Neighbor'),)
    STANDARD_ERRORS = (
        ('SIMPLE', 'simple'),
        ('CLUSTER', 'cluster'),
        ('BOOTSTRAP', 'bootstrap'),
        ('AI', 'Abadie and Imbens')
    )

    user = models.ForeignKey(User)
    usermap = models.ForeignKey(Map)
    matching_method = models.CharField(max_length=50, choices=METHODS)
    matching_estimator = models.CharField(max_length=50, choices=ESTIMATORS)
    covariate_variables = models.TextField(null=False)
    outcome_variables = models.TextField(null=False)
    caliper_distance = models.IntegerField()
    common_support = models.BooleanField()
    standard_error_type = models.CharField(max_length=50, choices=STANDARD_ERRORS)
    low_outcome_year = models.IntegerField(default=2007)
    high_outcome_year = models.IntegerField(default=2007)
    current = models.NullBooleanField(default=False)
    objects = JobManager()

    def process(self, data):
        """
        Runs a matching algorithm to produces matches
        needed for mapping and tables
        """
        logger.debug("Started a new match")
        # map_id = self.usermap
        # outcome = self.outcome_variables

        # logger.debug("Creating design matrix")
        # data.retrieve(map_id, outcome, self.covariate_variables)

        logger.debug("Running matching algorithm")
        # Move to PSM handling
        sma = StatisticalMatchingAdapter(matching_method='NN', matching_estimator='logit')
        sma.fit(data.treated_column, data.design_matrix, data.covariate_names)
        sma.match()
        logger.debug("Completed match")
        return sma

class JobStats(models.Model):
    job_id = models.ForeignKey(Job)
    created = models.DateTimeField(auto_now_add=True)
    session_start = models.DateTimeField()
    country = models.CharField(max_length=500, default='')
    region_type = models.CharField(max_length=50, default='')
    state = models.CharField(max_length=50, default='')
    min_forest_cover = models.CharField(max_length=50, default='')
    max_forest_cover = models.CharField(max_length=50, default='')
    agroforest = models.CharField(max_length=50, default='')
    agriculture = models.CharField(max_length=50, default='')
    forest = models.CharField(max_length=50, default='')
    treatment_area_option = models.CharField(max_length=50, default='')
    control_area_option = models.CharField(max_length=50, default='')
