'''
This module does very little aside from serve javascript 
because the app relies on an internal API and there is little reason
to make the front-end depend on django.
This could possibly be moved out as static files or the url can be
redirected to a static server such a nginx

The geoserver url routing could be improved and could possibly be
put into its own app if the the complexity of the routing expands
'''

from django.shortcuts import render
from django.shortcuts import render as render_to_response
from django.template import RequestContext
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests


# Views
def index(request):
    '''Serves the main html page responsible for loading the ExtJS app, ExtJS dependencies, and google map dependencies'''
    return render_to_response(
        template_name='first_page/index.html',
        request=request)


def app(request):
    '''Main app file. This loads all models, views, and controllers'''
    return render(request, 'app/app.js')


def viewport(request):
    '''This is the main view that loads in all others views and renders the front end.
    Here we determine the overall layout of the web page and fill in the details with other views'''
    return render(request, 'app/view/Viewport.js')


def main_map(request):
    '''View to display the main map. The map is rendered using OpenLayers and sends calls to GeoServer,
    and google maps API to get geospatial data. OpenLayers handles map controls such as zooming and panning.
    Geoserver generates the actual map tiles from the geospatial data stored in PostgreSQL.'''
    return render(request, 'app/view/MainMap.js')


## Side bar
def overview(request):
    '''View responsible for giving intro information to user'''
    return render(request, 'app/view/Overview.js')

def define_study_area(request):
    '''View responsible for selecting broad regions on the map'''
    return render(request, 'app/view/DefineStudyArea.js')


def define_study_years(request):
    '''
    View responsible for selecting the time range that the study will 
    account for
    '''
    return render(request, 'app/view/DefineStudyYears.js')


def limit_plot_types(request):
    '''
    View responsible for selecting classes of points to remove from 
    the study
    '''
    return render(request, 'app/view/LimitPlotTypes.js')


def select_policy_areas(request):
    '''
    View responsible for selecting tools such as shapefile upload,
    polygon selection, and policy selection in the context of 
    selecting treatment areas
    '''
    return render(request, 'app/view/SelectPolicyAreas.js')


def select_control_areas(request):
    '''
    View responsible for selection tools such as shapefile upload, 
    polygon selection, and policy selection in the context of 
    selecting controlled areas
    '''
    return render(request, 'app/view/SelectControlAreas.js')


def match_similar_plots(request):
    '''
    View responsible for selecting the parameters for matching and 
    initiating the matching algorithm
    '''
    return render(request, 'app/view/MatchSimilarPlots.js')


# These three views have considerably different data passed to them
def check_balance_statistics(request):
    '''
    View responsible for displaying balance statistics data output 
    from the matching procedure    
    '''
    return render(request, 'app/view/CheckBalanceStatistics.js')


def measure_treatment_effects(request):
    '''
    View resonsible for displaying the actual results from the 
    matching procedure
    '''
    return render(request, 'app/view/MeasureTreatmentEffects.js')


def check_sensitivity(request):
    '''
    View resonsible for displaying Rosenbaum bounds of Mantel-Haenzel bounds
    '''
    return render(request, 'app/view/CheckSensitivity.js')


def report(request):
    '''
    View responsible for giving a way to download a complete 
    report of matching    
    '''
    return render(request, 'app/view/Report.js')


# Javascript to render floating windows
def cs(request):
    '''Window related to Check Sensitivity'''
    return render(request, 'app/view/CS.js')


def msp(request):
    '''Window related to Match Similar Plots'''
    return render(request, 'app/view/MSP.js')


def mte(request):
    '''Window related to Results/Measure Treatment Effects'''
    return render(request, 'app/view/MTE.js')


# Models
# Needs to be refactored -- models are not well separated yet
def station_model(request):
    return render(request, 'app/model/Station.js')


def song(request):
    return render(request, 'app/model/Song.js')


# Stores
# Needs to be refactored -- stores are not well separated yet--probably won't be
def recent_songs_store(request):
    return render(request, 'app/store/RecentSongs.js')


def stations_store(request):
    return render(request, 'app/store/Stations.js')


def search_results_store(request):
    return render(request, 'app/store/SearchResults.js')


# Controllers
# Needs to be refactored -- controllers are not well separated yet
def station_controller(request):
    return render(request, 'app/controller/Station.js')


def song_controller(request):
    return render(request, 'app/controller/Song.js')


# Temporary view for geoserver
@csrf_exempt
def geoserver_wms(request):
    '''View to reroute geoserver requests to the geoserver server
    
    A typical request is roughly:
    http://172.20.3.80:8080/geoserver/evaluator/wms?
    LAYERS=evaluator:usermap&ISBASELAYER=false&WIDTH=1542&SERVICE=WMS&
    FORMAT=image/png&REQUEST=GetMap&
    HEIGHT=1497&STYLES=&SRS=EPSG:900913&
    VERSION=1.1.1&
    BBOX=-10762061.804957,1343052.0069406,-9819134.6241626,2258461.8575564&
    _OLSALT=0.6252261116169393&STRATEGIES=[object%20Object]&TRANSPARENT=TRUE    
    '''

    def calculate_sample_probability(bbox):
        left, bottom, right, top = [float(value) for value in bbox]
        total_area = (right - left) * (top - bottom)
        base_area = 500000000000 # Reference map area, corresponds to zoom level where we do no sampling
        min_sample = 0.01
        sample_rate = 0.10
        zoom_sample_rate = base_area/total_area
        assert min_sample > 0, 'Geoserver fails when sampling value is zero or negative'


        return sample_rate*(zoom_sample_rate) + min_sample

    if request.method == 'GET':
        params = (key + '=' + str(value)
                  for (key, value)
                  in request.GET.iteritems())

        bbox = request.GET.get('BBOX').split(',')
        sample_factor = calculate_sample_probability(bbox)
        hidden_params = '&viewparams=usermap:' + str(request.session['mid']) + ';' + \
                        'sample:' + str(sample_factor)
        base_url = 'http://127.0.0.1:8080/geoserver/evaluator/wms?'
        r = requests.get(base_url + '&'.join(params) + hidden_params)
        response = HttpResponse(content_type="image/gif")
        response.write(r.content)
        return response

    elif request.method == 'POST':
        params = (key + '=' + str(value)
                  for (key, value)
                  in request.GET.iteritems())

        hidden_params = '&viewparams=usermap:' + str(request.session['mid'])
        base_url = 'http://127.0.0.1:8080/geoserver/evaluator/wfs?'
        # r = requests.get(base_url + '&'.join(params) + hidden_params)
        r = requests.post(base_url + '&'.join(params) + hidden_params, data=request.body)
        response = HttpResponse(content_type="application/xml")
        response.write(r.text)
        return response


@csrf_exempt
def geoserver_wfs(request):
    '''View to reroute geoserver requests to the geoserver server

    A typical request is roughly:
    http://127.0.0.1:8080/geoserver/evaluator/wms?
    LAYERS=evaluator:usermap&ISBASELAYER=false&WIDTH=1542&SERVICE=WMS&
    FORMAT=image/png&REQUEST=GetMap&
    HEIGHT=1497&STYLES=&SRS=EPSG:900913&
    VERSION=1.1.1&
    BBOX=-10762061.804957,1343052.0069406,-9819134.6241626,2258461.8575564&
    _OLSALT=0.6252261116169393&STRATEGIES=[object%20Object]&TRANSPARENT=TRUE
    '''

    if request.method == 'POST':
        params = (key + '=' + str(value)
                  for (key, value)
                  in request.GET.iteritems())

        hidden_params = '&viewparams=usermap:' + str(request.session['mid'])
        base_url = 'http://127.0.0.1:8080/geoserver/evaluator/wfs?'
        # r = requests.get(base_url + '&'.join(params) + hidden_params)
        r = requests.post(base_url, data=request.body)
        response = HttpResponse(content_type="application/xml")
        response.write(r.text)
        return response


def geoserver_map(bbox, width, height, user_map):
    width = float(width)
    height = float(height)
    if width > height:
        map_scalar = float(500)/width
    else:
        map_scalar = float(500)/height
    base_url = 'http://127.0.0.1:8080/geoserver/evaluator/wms?'
    layers = 'LAYERS=evaluator%3Ausermap_fastfeature,evaluator%3Aregions_region&'
    styles = 'STYLES=,regions_for_pdf&'
    format = 'FORMAT=image%2Fpng&'
    transparent = 'TRANSPARENT=TRUE&'
    service = 'SERVICE=WMS&'
    request = 'REQUEST=GetMap&'
    srs = 'SRS=EPSG%3A900913&'
    bbox = 'BBOX='+ bbox +'&'
    width = 'WIDTH=' + str(int(width*map_scalar)) + '&'
    height = 'HEIGHT=' + str(int(height*map_scalar)) + '&'
    hidden_params = 'viewparams=usermap:' + str(user_map.id)

    request_url = base_url + layers + styles + format + transparent + service + request + srs + bbox + width + height + hidden_params

    return request_url

