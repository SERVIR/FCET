from .models import CBSmeans, CBStests, Results, ResultsChart, CheckSensitivity
from collections import OrderedDict
import layers.services as layer_services

def get_balance_statistics_means(user_map):
    return CBSmeans.objects.get_table(user_map)


def get_balance_statistics_tests(user_map):
    return CBStests.objects.get_table(user_map)

def get_summary_statistics_table(user_map):
    return CBStests.objects.get_table_as_list(user_map)


def get_balance_statistics_means_unmatched(user_map):
    means = get_balance_statistics_means(user_map)
    # Have to convert Decimals to float since reportlab won't support Decimal type
    return [float(mean.bias) for mean in means if mean.sample == 'Unmatched']


def get_balance_statistics_means_matched(user_map):
    means = get_balance_statistics_means(user_map)
    # Have to convert Decimals to float since reportlab won't support Decimal type
    return [float(mean.bias) for mean in means if mean.sample == 'Matched']


def get_balance_statistics_var_names(user_map):
    means = get_balance_statistics_means(user_map)
    ordered_unique = OrderedDict.fromkeys([mean.name for mean in means])
    return [layer_services.legible_covariate_names(var) for var in list(ordered_unique)]

def get_balance_statistics_table(user_map):
    cbs_means = CBSmeans.objects.get_table(user_map)
    return [[layer_services.legible_covariate_names(row.name),
             row.sample,
             row.treated,
             row.control,
             row.bias,
             row.biasr,
             row.t,
             row.pt]
            for row in cbs_means]


def get_results_table(user_map):
    return Results.objects.get_table(user_map)


def get_results_table_as_list(user_map):
    return Results.objects.get_table_as_list(user_map)


def get_results_chart(user_map):
    return ResultsChart.objects.get_table(user_map)


def get_results_chart_as_dict(user_map):
    results = get_results_chart(user_map)
    return {res.name: res.data_values for res in results}


def get_sensitivity_results(user_map):
    return CheckSensitivity.objects.get_table(user_map)
