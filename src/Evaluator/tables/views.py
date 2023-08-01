from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from tables.models import CBSmeans, CBStests, Results, ResultsChart, CheckSensitivity
import tables.serializers as serializers
import tables.services as table_services
from django.contrib.auth.models import User
from map.models import Map

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its contents in JSON
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
        
@csrf_exempt
def cbs_means(request):
    """
    List all enteries in the CBS means table
    """
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        means = table_services.get_balance_statistics_means(user_map)
        serializer = serializers.CBSmeansSerializer(means, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        return JSONResponse(serializer.errors, status=400)

def cbs_tests(request):
    """
    List all enteries in the CBS means table
    """
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        means = table_services.get_balance_statistics_tests(user_map)
        serializer = serializers.CBStestsSerializer(means, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        return JSONResponse(serializer.errors, status=400)
        
@csrf_exempt
def results(request):
    """
    List all enteries in the CBS means table
    """
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        means = table_services.get_results_table(user_map)
        serializer = serializers.ResultsSerializer(means, many=True)
        return JSONResponse(serializer.data, status=200)
        
    elif request.method == 'POST':
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def results_chart(request):
    """
    List all enteries in the CBS means table
    """
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        means = table_services.get_results_chart(user_map)
        serializer = serializers.ResultsChartSerializer(means, many=True)
        return JSONResponse(serializer.data, status=200)
        
    elif request.method == 'POST':
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def check_sensitivity(request):
    """
    List all enteries in the check sensitivity table
    """
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        means = table_services.get_sensitivity_results(user_map)
        serializer = serializers.CheckSensitivitySerializer(means, many=True)
        return JSONResponse(serializer.data, status=200)

    elif request.method == 'POST':
        return JSONResponse(serializer.errors, status=400)
