from django.db import models
from django.contrib.auth.models import User


class PSM(models.Model):
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
    
    #HINT: ForeignKey(unique=True) is usually better served by a OneToOneField.
    #TODO: Change to auth user
    user = models.ForeignKey(User)
    matching_method = models.CharField(max_length = 50, choices = METHODS)
    matching_estimator = models.CharField(max_length = 50,
                                          choices = ESTIMATORS)
    #Excepts a list
    covariate_variables = models.TextField(null = False)
    #Excepts a list
    outcome_variables = models.TextField(null = False)
    caliper_distance = models.IntegerField()
    common_support = models.BooleanField()
    standard_error_type = models.CharField(max_length = 50, 
                                           choices = STANDARD_ERRORS)
