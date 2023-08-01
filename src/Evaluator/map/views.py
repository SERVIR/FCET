from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
# available_attrs was a Python 2-3 compatability function
# from django.utils.decorators import available_attrs
from django.http import HttpResponse
from layers.models import Feature, Attribute, AttributeValue
from django.db import transaction
import regions.services as region_services
import layers.services as layer_services
import map.services as map_services
from map import utils as shape_utils
from map.models import ShapeFileUpload, UserSession, Map
from tables import services as table_services
import logging
from django.core.cache import cache
from .pdf_generation import generate_results_report
from django.utils.timezone import now
from django.utils.dateformat import DateFormat
from first_page.views import geoserver_map
from jobs.views import clear_job
from Evaluator.settings import BASE_DIR
import os
import json
logger = logging.getLogger(__name__)


def login_required(function=None):
    """
    Decorator for views that checks that the user is authenticated, sends 401 unauthorized response if not.
    """

    def test_func(user):
        return user.is_authenticated()

    def decorator(view_func):
        # available_attrs was a Python 2-3 compatability function
        # @wraps(view_func, assigned=available_attrs(view_func))
        wraps(view_func)

        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Unauthorized', status=401)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


# def map_features(request):
#     """Associates features and related attributes to a user's map"""
#     user = User.objects.filter(username='test')[0]
#     features = Feature.objects.order_by('id').all()
#     user_map = user.map
#     layer_services.collect_features(user_map, features, 500)
#     return HttpResponse('Success', status=200)

@csrf_exempt
def map_region(request, fid):
    user_map = Map.objects.get(pk=request.session['mid'])

    feature_ids = cache.get(' '.join(('region', fid)).replace(' ', '_'))
    feature_ids = map_services.get_points_by_region(fid)
    layer_services.collect_feature_ids(user_map, feature_ids, 60000)
    #layer_services.set_forest_cover_filter(user_map, 1, 100)
    return HttpResponse('Success', status=200)


@csrf_exempt
def unmap_region(request, fid):
    user_map = Map.objects.get(pk=request.session['mid'])

    feature_ids = map_services.get_points_by_region(fid)
    layer_services.unselect_features(user_map, feature_ids)
    return HttpResponse('Success', status=200)


@csrf_exempt
def map_chiapas(request):
    logger.debug("Loading Chiapas")
    user = User.objects.filter(username='test')[0]
    user_map = user.map
    logger.debug("Getting Attribute ID")
    attribute_id = Attribute.objects.get(name='state').id
    logger.debug("Getting Feature IDs")
    feature_ids = list(
        AttributeValue.objects.filter(
            attribute_id=attribute_id, value='Chiapas').values_list(
            'feature_id', flat=True))
    logger.debug("Updating Map")
    layer_services.collect_feature_ids(user_map, feature_ids, 60000)
    logger.debug("Finished Update")
    return HttpResponse('Success', status=200)


def clear_map(request):
    """
    Clear the user's map of all features.
    """
    user_map = Map.objects.get(pk=request.session['mid'])
    layer_services.clear_selected_points(user_map)
    layer_services.clear_treatment_points(user_map)
    layer_services.clear_control_points(user_map)
    layer_services.clear_forest_cover_filter(user_map)
    return HttpResponse('Success', status=200)


@csrf_exempt
def filter_forest_cover(request, lower_bound, upper_bound):
    """
    Filter loaded features by forest cover percentage, keep only the ones that fall in range.

    :param request: Django request object
    :param lower_bound: The lower bound of forest cover to keep
    :param upper_bound: The upper bound of forest cover to keep
    :return: HttpStatus
    """
    user_map = Map.objects.get(pk=request.session['mid'])
    layer_services.set_forest_cover_filter(user_map, lower_bound, upper_bound)

    return HttpResponse('Success', status=200)


@csrf_exempt
def clear_forest_cover_filter(request):
    """
    :param request: Django request object that track the user session
    :return: None, do I/O
    """
    # Call method from feature status manager that resets the forest cover filter to default values
    user_map = Map.objects.get(pk=request.session['mid'])
    layer_services.clear_forest_cover_filter(user_map)


@csrf_exempt
def select_treatment(request):
    """Select or flag treatment plots in the database"""
    if request.method == 'POST':
        user_map = Map.objects.get(pk=request.session['mid'])
        polygons = shape_utils.geojson_to_polygons(request.body, 3857, 4326)
        mpoly = shape_utils.polygons_to_mpoly(polygons)
        layer_services.set_treatment_points(user_map, mpoly)
        return HttpResponse(mpoly.geojson)
    else:
        return HttpResponse('Fail')


@csrf_exempt
def select_protected_areas(request):
    if request.method == "GET":
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.select_protected_areas(user_map)
        return HttpResponse('Success', status=200)


@csrf_exempt
def policy_areas(request):
    if request.method == "GET":
        json_response = json.dumps(region_services.get_policy_areas())
        return HttpResponse(json_response, status=200)

    if request.method == "POST":
        policy_name = json.loads(request.body)['policy_name']
        user_map = Map.objects.get(pk=request.session['mid'])
        points = map_services.get_points_by_policy(policy_name)
        layer_services.set_treatment_points_correct(user_map, points)
        return HttpResponse('Success', status=200)


def clear_treatment(request):
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.clear_treatment_points(user_map)
        return HttpResponse('Success', status=200)


@csrf_exempt
def select_control(request):
    """Select or flag treatment plots in the database"""
    if request.method == 'POST':
        user_map = Map.objects.get(pk=request.session['mid'])
        polygons = shape_utils.geojson_to_polygons(request.body, 3857, 4326)
        mpoly = shape_utils.polygons_to_mpoly(polygons)
        layer_services.set_control_points(user_map, mpoly)
        return HttpResponse(mpoly.geojson)
    else:
        return HttpResponse('Fail')


@csrf_exempt
def select_control_by_radius(request, lower, upper):
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.set_control_points_by_radius(user_map, lower, upper)
        return HttpResponse('Success', status=200)
    else:
        return HttpResponse('Fail')


@csrf_exempt
def select_control_by_exclude_spillovers(request, upper):
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.set_control_points_remove_spillovers(user_map, upper)
        return HttpResponse('Success', status=200)
    else:
        return HttpResponse('Fail')


@csrf_exempt
def select_control_points_by_study_area(request):
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.set_control_points_by_study_area(user_map)
        return HttpResponse('Success', status=200)
    else:
        return HttpResponse('Fail')


def clear_control(request):
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.clear_control_points(user_map)
        return HttpResponse('Success', status=200)


def clear_matched(request):
    if request.method == 'GET':
        user_map = Map.objects.get(pk=request.session['mid'])
        layer_services.clear_matched_points(user_map)
        clear_job(request)
        return HttpResponse('Success', status=200)


def reset_map_setting(request):
    """
    Resets all data associated with a map to default.
    This is to allow user to start from the beginning of the matching process
    """

    # Reset map
    clear_map(request)
    # Reset forest filter
    clear_forest_cover_filter(request)
    # Reset treatment areas
    clear_treatment(request)
    # Reset control areas
    clear_control(request)
    # Reset matches
    clear_matched(request)
    # Reset job
    clear_job(request)
    return HttpResponse("Success", status=200)


@csrf_exempt
def user_login(request):
    # Refactor this into a users/auth app if the logic grows
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            response = '{"success": true, "msg": "You are logged in."}'
            return HttpResponse(response, status=200)
        else:
            assert False, str("We should not have any inactive users")
    else:
        return HttpResponse("Permission Denied", status=403)

@csrf_exempt
def get_session(request):
    if not request.session.get('has_session'):
        request.session['has_session'] = True
        map = Map.objects.create()
        request.session['mid'] = map.id

    return HttpResponse('success', status=200)

@csrf_exempt
def shp_to_geojson(request):
    """
    Accept shapefile from user and return GeoJSON Polygons

    :param request:
    :return:
    """
    if request.method == 'POST':
        # Retrieve shapefile data from POST
        shapefile = request.FILES['shapefile']
        indexfile = request.FILES['indexfile']
        datafile = request.FILES['datafile']
        prjfile = request.FILES.get('prjfile', None)

        # Check against filesize limit
        for uploaded_file in [shapefile, indexfile, datafile]:
            MAX_FILE_SIZE = 5*1024*1024 #MB converted to bytes
            if uploaded_file.size > MAX_FILE_SIZE:
                return HttpResponse(
                        {"success": "false",
                         "message": "Files cannot be larger than %s MB" % (MAX_FILE_SIZE/1024/1024)},
                        status=400)

        # Check extension of every file uploaded through POST
        def extension_is_not(target_ext, filename):
            """
            Return True if file extension does not match the expected extension
            """
            name, _, ext = filename.rpartition('.')
            return ext != target_ext

        if extension_is_not('shp', shapefile.name):
            return HttpResponse({"success": "false", "message": "Shapefile extension must be .shp"}, status=400)
        if extension_is_not('shx', indexfile.name):
            return HttpResponse({"success": "false", "message": "Index file extension must be .shx"}, status=400)
        if extension_is_not('dbf', datafile.name):
            return HttpResponse({"success": "false", "message": "Attribute file extension must be .dbf"}, status=400)
        if prjfile:
            if extension_is_not('prj', prjfile.name):
                return HttpResponse({"success": "false", "message": "Projection file extension must be .prj"}, status=400)

        # Save files to disk and track in database
        if prjfile:
            user_shp = ShapeFileUpload(shapefile=shapefile, indexfile=indexfile, datafile=datafile, prjfile=prjfile)
            user_shp.save()
        else:
            user_shp = ShapeFileUpload(shapefile=shapefile, indexfile=indexfile, datafile=datafile)
            user_shp.save()

        # Attempt to read shapefile
        #try:
        layer = user_shp.load_shapefile()
        #except:
        #    return HttpResponse(
        #            shape_utils.as_json({"success": "false", "message": "Could not read shapefile"}),
        #            status=400)

        # Fail if shapefile does not contain polygons
        if not shape_utils.is_polygon(layer):
            return HttpResponse(
                    shape_utils.as_json({"success": "false", "message": "Shapefile geometry should be Polygon"}),
                    status=400)

        # Convert shapefile to geojson to be rendered on the client side
        geojson = shape_utils.shapefile_to_geojson(layer)
        return HttpResponse(shape_utils.as_json({"success": "True", "message": "Success", "geojson": geojson}), status=200)


@csrf_exempt
def create_report(request, bbox, width, height):
    """
    Create PDF that displays the results of the previous job that was run by the user
    :param request:
    :return:
    """
    user_map = Map.objects.get(pk=request.session['mid'])
    job = user_map.job_set.most_recent(user_map)
    if job:
        job = job[0]
        job_stats = job.jobstats_set.get()
        report_generated_time = DateFormat(now()).format('jS F Y H:i e')

        response = HttpResponse(content_type='application/pdf')
        report_filename = 'FCET_{region}_{report_generated_time}'.format(
            region=job_stats.state,
            report_generated_time=report_generated_time.replace(' ', '_'))
        response['Content-Disposition'] = 'attachment; filename={filename}.pdf'.format(filename=report_filename)
        results_chart = table_services.get_results_chart_as_dict(user_map)
        results_data = table_services.get_results_table_as_list(user_map)

        fields = {
            'country': job_stats.country.encode('utf8'),
            'region_type': job_stats.region_type,
            'state': job_stats.state,
            'start_year': job.low_outcome_year,
            'end_year': job.high_outcome_year,
            'min_forest_cover': job_stats.min_forest_cover,
            'max_forest_cover': job_stats.max_forest_cover,
            'agroforest': job_stats.agroforest,
            'agriculture': job_stats.agriculture,
            'forest': job_stats.forest,
            'treatment_area_option': job_stats.treatment_area_option,
            'control_area_option': job_stats.control_area_option,
            'matching_method': job.matching_method,
            'matching_estimator': job.matching_estimator,
            'covariates': [layer_services.legible_covariate_names(cov) for cov in job.covariate_variables.split(',')],
            'caliper': job.caliper_distance,
            'common_support': job.common_support,
            'standard_errors': job.standard_error_type,
            'control_mean': results_chart['Unmatched Control'],
            'match_mean': results_chart['Matched Control'],
            'treated_mean': results_chart['Treatment'],
            'att': results_chart['ATT'],
            'results_data': results_data,
            'summary_statistics_data': table_services.get_summary_statistics_table(user_map),
            'balance_statistics_data': table_services.get_balance_statistics_table(user_map),
            'balance_statistics_means_unmatched': table_services.get_balance_statistics_means_unmatched(user_map),
            'balance_statistics_means_matched': table_services.get_balance_statistics_means_matched(user_map),
            'balance_statistics_var_names': table_services.get_balance_statistics_var_names(user_map),
            'session_start_time': DateFormat(job_stats.session_start).format('jS F Y H:i e'),
            'report_generated_time': report_generated_time,
            'map_url': geoserver_map(bbox, width, height, user_map)
        }
        generate_results_report(response, fields)
        pdf_location = os.path.join(BASE_DIR, 'reports', report_filename + '_' + str(job.id) + '.pdf')
        # with open(pdf_location, 'w+') as out_file:
        #     out_file.write(response.content)
        #     out_file.close()
        return response
    else:
        return HttpResponse('Please run a match before attempting to generate a report', status=400)
