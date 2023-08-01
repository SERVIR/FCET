from django.urls import re_path as url
from regions import views

urlpatterns = [
    url(r'^show', views.get_regions),
    url(r'^all', views.get_all),
]
