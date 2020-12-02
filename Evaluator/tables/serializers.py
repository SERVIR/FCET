from rest_framework import serializers
from tables.models import CBSmeans, CBStests, Results, ResultsChart, CheckSensitivity
from layers.services import legible_covariate_names

class CBSmeansSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = CBSmeans
        fields = ['id',
                  'name',
                  'sample',
                  'treated',
                  'control',
                  'bias',
                  'biasr',
                  't',
                  'pt']

    def get_name(self, obj):
        return legible_covariate_names(obj.name)

class CBStestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBStests
        fields = ['sample',
                  'pseudo_r2',
                  'LR_chi2',
                  'chi2_pvalue',
                  'mean_bias',
                  'med_bias']


class ResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Results
        fields = ['id',
                  'variable',
                  'sample',
                  'treated',
                  'controls',
                  'difference',
                  't_stat',
                  'standard_error']


class ResultsChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultsChart
        fields = ['id', 'name', 'data_values']


class CheckSensitivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckSensitivity
        fields = ['gamma',
                  'q_plus',
                  'q_minus',
                  'p_plus',
                  'p_minus']
