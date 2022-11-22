# -*- coding: utf-8 -*-

from django.urls import re_path as url
from jobs import views
#JOB_URL = r'^new/' + '(?P<caliper>[0-9]{1,3})/' + \
#    '(?P<support>true|false)/' + \
#    '(?P<covariates>[A-Za-z0-9,_]+)/' + \
#    '(?P<estimator>[A-Z]{1,2})/' + \
#    '(?P<method>[A-Z]{2,3})/' + \
#    '(?P<outcome>[A-Za-z0-9_]+)/' + \
#    '(?P<low_outcome_year>[0-9]+)/' + \
#    '(?P<high_outcome_year>[0-9]+)/' + \
#    '(?P<error_type>[A-Z]{2,9})/' + \
#    '$'
JOB_URL = r'new/$'

urlpatterns  = [
    url(JOB_URL, views.create_job),
    url(r'clear/$', views.clear_job),
]
