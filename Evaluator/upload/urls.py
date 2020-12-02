from django.conf.urls import url
from upload import views

urlpatterns  = [
    url(r'^up/$', views.upload_file, name="upload_file"),
    url(r'^createuser/$', views.create_user),
]
