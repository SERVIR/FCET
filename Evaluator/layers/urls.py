from django.conf.urls import url
from layers import views

urlpatterns  = [
    url(r'^covariates$', views.covariates),
]
