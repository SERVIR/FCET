from django.db import models
from django.contrib.gis.db import models as geomodels
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.gis.gdal import DataSource
import uuid
import os

def get_file_path(instance, filename):
    # Generate filename that's identical for each part of the shapefile
    name, _, ext = filename.rpartition('.')
    name = str(name) + str(instance.uid) # deal with encodings and ensure names are unique
    filename = "%s.%s" % (uuid.uuid3(uuid.NAMESPACE_DNS, name), ext)
    return os.path.join('user_shapefiles', filename)

class Map(models.Model):
    SRID = 4326
    #user = models.OneToOneField(User, unique=True)

class ShapeFileUpload(models.Model):
    shapefile = models.FileField(upload_to=get_file_path)
    indexfile = models.FileField(upload_to=get_file_path)
    datafile = models.FileField(upload_to=get_file_path)
    prjfile = models.FileField(upload_to=get_file_path, null=True)
    uid = models.CharField(max_length=64, default=uuid.uuid4)

    def load_shapefile(self):
        #data_path = os.path.join(settings.BASE_DIR, self.shapefile.name)
        data_path = os.path.join(self.shapefile.name)
        ds = DataSource(data_path)
        layer = ds[0]
        return layer

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
