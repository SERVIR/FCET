from django.shortcuts import render as render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from .forms import UploadFileForm
from layers.models import UploadFile
from django.contrib.auth.models import User

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

def upload_file(request):
    if request.method == 'POST':
        #if request.FILES==None:
        #    raise Http404("No objects uploaded")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            #TODO: Detect user from request
            user = User.objects.filter(username='test')[0]
            upload = user.upload_set.create(geom_type='geom', encoding='enc')
            upload.uploadfile_set.create(upload_file=request.FILES['upload_file'])
            #Eventaully replace with file location from 
            #upload instance...in the model class.. it knows the location...
            data_location = '/home/vagrant/public_html/Evaluator/domain1.com/Evaluator/uploads/mex_1km_foralex.shp'
            upload.upload_features(data_location)
            return HttpResponseRedirect(reverse('upload.views.upload_file'))
    else:
        form = UploadFileForm()
        files = UploadFile.objects.all()
    return render_to_response('upload.html', {'form':form, 'files':files}, 
                              context_instance=RequestContext(request))

def test_file_upload(data_location, slice_stop):
    user = User.objects.filter(username='test')[0]
    upload = user.upload_set.create(geom_type='geom', encoding='enc')
    # upload.uploadfile_set.create(upload_file=request.FILES['upload_file'])
    # data_location = '/home/vagrant/Evaluator/Evaluator/domain1.com/Evaluator/uploads/mex_1km_foralex.shp'
    upload.upload_features(data_location, slice_stop=slice_stop)


def create_user(request):
    #TODO: Get this view into a proper location
    if request.method == 'GET': #change this request type...it is silly
        #This should now be broken and needs to be replaced with signals
        user = User.objects.create_user('test', 'test@tester.com', 'password')
        user.last_name = 'tested'
        user.save()
        user.map_set.create()
        return HttpResponse('Success')
    else:
        return HttpResponse('Wrong request method')
#==============================================================================
# def handle_uploaded_file(f):
#     import os
#     from django.contrib.gis.gdal import DataSource
#     from django.contrib.gis.geos GEOSGeomentry
#     from layers.models import Feature
#     from upload.models import UploadFile
#     ds = DataSource('/home/vagrant/public_html/Evaluator/domain1.com/Evaluator/uploads/mex_1km_foralex.shp')
#     layer = ds[0]
#     feature = layer[0]
#     from django.contrib.auth.models import User
#     user = User.objects.all()[1]
#     user.map_set
#     #upload = UploadFile.objects.all()[1]
#     
#     Feature.add_feature(user.id, GEOSGeomentry(feature.geom), upload.upload_id)
#==============================================================================
    
    
