from django.http import HttpResponse
from layers.models import Attribute, AttributeValue
from django.contrib.auth.models import User
from map.models import Map
from layers.serializers import AttributeNameSerializer
from rest_framework.renderers import JSONRenderer
import layers.services as layer_services


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its contents in JSON
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def covariates(request):
    """Return json list of all covariates belonging to user"""    

    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])

        approved_attributes = layer_services.APPROVED_COVARIATES.keys()
        selected_features = layer_services.get_selected_points(user_map)
        selected_attributes = AttributeValue.objects.filter(feature_id__in=selected_features[:1])\
            .distinct('attribute_id')\
            .values_list('attribute_id', flat=True)
        attributes = Attribute.objects.filter(name__in=approved_attributes, id__in=selected_attributes)
        serializer = AttributeNameSerializer(attributes, many=True)
        return JSONResponse(serializer.data, status=200)
        
    elif request.method == 'POST':
        return JSONResponse(serializer.errors, status=400)


def create_point_features(data_location, slice_stop):
    user = User.objects.filter(username='test')[0]
    upload = user.upload_set.create(geom_type='geom', encoding='enc')
    upload.upload_features(data_location, slice_stop=slice_stop)
