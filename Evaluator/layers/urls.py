from django.urls import re_path as url
from layers import views

urlpatterns  = [
    url(r'^covariates$', views.covariates),
]
