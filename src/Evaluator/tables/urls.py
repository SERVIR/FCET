from django.urls import re_path as url
from tables import views

urlpatterns  = [
    url(r'^cbsmeans/$', views.cbs_means),
    url(r'^cbstests/$', views.cbs_tests),
    url(r'^results/$', views.results),
    url(r'^resultschart/$', views.results_chart),
    url(r'^checksensitivity/$', views.check_sensitivity),
]
