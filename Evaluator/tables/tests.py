from django.test import TestCase
from django.test.client import RequestFactory
from tables.models import CBSmeans, Results, ResultsChart
from django.contrib.auth.models import User
from jobs.services import StatisticalMatchingAdapter
from jobs.models import Job
from tables.views import results_chart

#
# Outdate, fix or delete
#
#

class CBSmeansTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='test')
        self.job = Job(user=self.user,
                  caliper_distance=0, 
                  common_support='true', 
                  covariate_variables='forest_cov,dis_to_cit', 
                  matching_estimator='NN', 
                  matching_method='PSM',
                  outcome_variables='forest_cov', 
                  standard_error_type='SIMPLE')
        self.job.save()
    
    def test_create_table_should_create_CBSmean_entry(self):
        sma = StatisticalMatchingAdapter()
        sma.att = 0
        sma.matched_control_mean = 0
        sma.matched_treated_mean = 0
        sma.unmatched_control_mean = 0
        sma.unmatched_treated_mean = 0
        CBSmeans.objects.create_table(self.job, sma)
        self.assertIsInstance(CBSmeans.objects.first(), CBSmeans)

    def test_get_table_is_not_empty(self):
        psm = psm = make_psm_object(
            header = ['ttime_min', 'slope'],
            data =  [[10, 1],[10, 1], [10, 1], [10, 1], [5, 1]], 
            index = [0, 1, 2, 3, 4],
            columns = ['0', '1'],
            treated = [1, 1, 0, 0, 0],
            matches = [2,3],
            weights = [0, 0, 1, 1, 0])
        psm.att = 0
        psm.matched_control_mean = 0
        psm.matched_treated_mean = 0
        psm.unmatched_control_mean = 0
        psm.unmatched_treated_mean = 0
        CBSmeans.objects.fit(self.job, psm)
        means = CBSmeans.objects.get_table(self.user)
        self.assertNotEqual(len(means), 0)        
        
    def test_cbsmeans_table_is_correct(self):
        psm = psm = make_psm_object(
            header = ['ttime_min', 'slope'],
            data =  [[10, 1],[10, 1], [10, 1], [10, 1], [5, 1]], 
            index = [0, 1, 2, 3, 4],
            columns = ['0', '1'],
            treated = [1, 1, 0, 0, 0],
            matches = [2,3],
            weights = [0, 0, 1, 1, 0])
        psm.att = 0
        CBSmeans.objects.fit(self.job, psm)
        
        true_dict = {
            'slope': {'treated': 1.0, 
                      'unmatched': 1.0, 
                      'matched': 1.0}, 
            'ttime_min': {
                        'treated': 10.0, 
                        'unmatched': 8.333333333333334, 
                        'matched': 10.0}}
                        
        means = CBSmeans.objects.get_table(self.user)[:]
        for entry in means:
            mean_values = true_dict[entry.name]
            assert mean_values['treated']==entry.treated
            if entry.sample == 'Unmatched':
                self.assertAlmostEqual(mean_values['unmatched'],
                                       float(entry.control), 5)
            elif entry.sample == 'Matched':
                self.assertAlmostEqual(mean_values['matched'], 
                                       float(entry.control), 5)
            else:
                raise Exception('Sample value is incorrect')

class ResultsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='test')
        self.job = job = Job(user=self.user,
                  caliper_distance=0, 
                  common_support='true', 
                  covariate_variables='forest_cov,dis_to_cit', 
                  matching_estimator='NN', 
                  matching_method='PSM',
                  outcome_variables='forest_cov', 
                  standard_error_type='SIMPLE')
        job.save()
        
    def test_result_fit_should_create_results_entry(self):
        psm = PropensityScoreMatching()
        psm.att = 0
        psm.matched_control_mean = 0
        psm.matched_treated_mean = 0
        psm.matched_se = 0
        psm.matched_tstat = 0
        psm.unmatched_control_mean = 0
        psm.unmatched_treated_mean = 0
        psm.unmatched_se = 0
        psm.unmatched_tstat = 0
        Results.objects.fit(self.job, psm)
        self.assertIsInstance(Results.objects.first(), Results)
        
    def test_results_should_match_psm_means(self):
        psm = PropensityScoreMatching()
        psm.att = 65
        psm.matched_control_mean = 465
        psm.matched_treated_mean = 35
        psm.matched_se = 0
        psm.matched_tstat = 0
        psm.unmatched_control_mean = 564
        psm.unmatched_treated_mean = 654
        psm.unmatched_se = 0
        psm.unmatched_tstat = 0
        test_set = (psm.matched_control_mean,
                     psm.matched_treated_mean,
                     psm.unmatched_control_mean,
                     psm.unmatched_treated_mean)
        Results.objects.fit(self.job, psm)
        res = Results.objects.all()
        unmatched = res[0]
        att = res[1]
        return_set = (att.controls,
                      att.treated,
                      unmatched.controls, 
                      unmatched.treated)
        self.assertEqual(test_set, return_set)
        
    def test_get_table_is_not_empty(self):
        psm = PropensityScoreMatching()
        psm.att = 0
        psm.matched_control_mean = 0
        psm.matched_treated_mean = 0
        psm.matched_se = 0
        psm.matched_tstat = 0
        psm.unmatched_control_mean = 0
        psm.unmatched_treated_mean = 0
        psm.unmatched_se = 0
        psm.unmatched_tstat = 0
        Results.objects.fit(self.job, psm)
        means = Results.objects.get_table(self.user)
        self.assertNotEqual(len(means), 0)

class ResultsChartTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(username='test')
        self.job = job = Job(user=self.user,
                  caliper_distance=0, 
                  common_support='true', 
                  covariate_variables='forest_cov,dis_to_cit', 
                  matching_estimator='NN', 
                  matching_method='PSM',
                  outcome_variables='forest_cov', 
                  standard_error_type='SIMPLE')
        job.save()
        
    def test_resultchart_fit_should_create_results_entry(self):
        psm = PropensityScoreMatching()
        psm.att = 0
        psm.matched_control_mean = 0
        psm.matched_treated_mean = 0
        psm.unmatched_control_mean = 0
        psm.unmatched_treated_mean = 0
        psm.unmatched_se = 0
        ResultsChart.objects.fit(self.job, psm)
        self.assertIsInstance(ResultsChart.objects.first(), ResultsChart)
        
    def test_get_table_is_not_empty(self):
        psm = PropensityScoreMatching()
        psm.att = 0
        psm.matched_control_mean = 0
        psm.matched_treated_mean = 0
        psm.unmatched_control_mean = 0
        psm.unmatched_treated_mean = 0
        psm.unmatched_se = 0
        ResultsChart.objects.fit(self.job, psm)
        means = ResultsChart.objects.get_table(self.user)
        self.assertNotEqual(len(means), 0)
        
    def test_resultschart_view(self):
        request = self.factory.get('/tables/resultschart/')
        results_chart(request)
