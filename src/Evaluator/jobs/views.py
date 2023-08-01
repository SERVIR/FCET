from django.shortcuts import render
from django.contrib.auth.models import User
from map.models import Map
from django.http import HttpResponse
from jobs.services import Data, AbstractFeature
from jobs.models import Job, JobStats
from tables.models import CBSmeans, CBStests, Results, CheckSensitivity, ResultsChart
from pickle import load
from Evaluator.settings import BASE_DIR
import layers.services as layer_services
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.utils import timezone
from django.db import transaction


@csrf_exempt
@transaction.atomic
def create_job(request):

    body = json.loads(request.body.decode("utf-8"))
    user_map = Map.objects.get(pk=request.session['mid'])
    _clear_job(user_map)

    caliper = body['caliper']
    support = (body['support'] == "true") # Fix boolean string parsing
    covariates = body['covariates']
    estimator = body['estimator']
    method = body['method']
    outcome = body['outcome']
    low_outcome_year = body['low_outcome_year']
    high_outcome_year = body['high_outcome_year']
    error_type = body['error_type']

    country = body['country'].encode('latin1')
    region_type = body['region_type']
    state = body['state']
    min_forest_cover = body['min_forest_cover']
    max_forest_cover = body['max_forest_cover']
    agroforest = body['agroforest']
    agriculture = body['agriculture']
    forest = body['forest']
    treatment_area_option = body['treatment_area_option']
    control_area_option = body['control_area_option']
    session_start = datetime.fromtimestamp(int(body['user_start_time'])/1000, timezone.utc) # Convert epoch ms to seconds

    # This user instance does not affect other user identification since we use usermap for identification
    user = User.objects.get(username='test')
    layer_services.clear_matched_points(user_map)
    job = Job(user=user,
              usermap=user_map,
              caliper_distance=caliper,
              common_support=support,
              covariate_variables=covariates,
              matching_estimator=estimator,
              matching_method=method,
              outcome_variables=outcome,
              standard_error_type=error_type,
              low_outcome_year=low_outcome_year,
              high_outcome_year=high_outcome_year,
              current=True)
    job.save()

    job_stats = JobStats(
            job_id=job,
            country=country,
            session_start=session_start,
            region_type=region_type,
            state=state,
            min_forest_cover=min_forest_cover,
            max_forest_cover=max_forest_cover,
            agroforest=agroforest,
            agriculture=agriculture,
            forest=forest,
            treatment_area_option=treatment_area_option,
            control_area_option=control_area_option
    )
    job_stats.save()

    abstractfeature = AbstractFeature()
    data = Data(abstractfeature)
    data.retrieve(user_map, job.outcome_variables, job.covariate_variables)
    stat_match = job.process(data)

    matched_feature_ids = stat_match.matches
    layer_services.set_matched_points(user_map, matched_feature_ids)

    # While the outcome variable could be assigned to stat_match,
    # this lets us change the outcome without refitting the match
    results = stat_match.results(data.outcome_column(job.low_outcome_year, job.high_outcome_year))
    balance_statistics = stat_match.balance_statistics()
    bounds = stat_match.bounds(data.outcome_column(job.low_outcome_year, job.high_outcome_year))
    
    CBSmeans.objects.create_table(job, balance_statistics)    
    CBStests.objects.create_table(job, balance_statistics)
    # Results.objects.create_table(job, results, data.outcome_names[0])
    Results.objects.create_table(job, results, "Forest Loss")
    # ResultsChart.objects.create_table(job, results, data.outcome_names[0])
    ResultsChart.objects.create_table(job, results, "Forest Loss")
    CheckSensitivity.objects.create_table(job, bounds)
    return HttpResponse('success', status=200)

def _clear_job(user_map):
    job = Job.objects.most_recent(user_map)
    if job:
        job = job[0]
        job.current = False
        job.save()

def clear_job(request):
    user_map = Map.objects.get(pk=request.session['mid'])
    _clear_job(user_map)
    return HttpResponse('success', status=200)
