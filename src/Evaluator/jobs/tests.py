from django.test import TestCase
from django.test.client import RequestFactory
import jobs.views as view
from jobs.models import Job
from tables.models import CBSmeans, Results, ResultsChart
from django.contrib.auth.models import User
from jobs.psm import PropensityScoreMatching, MatchingResults
from map.models import Map
from layers.models import Feature, FeatureStatus
import layers.services as layer_services
from numpy import isnan, asarray, where
from pandas import DataFrame, Series
from jobs.services import Data, AbstractFeature, StatisticalMatchingAdapter
from numpy import array

class JobTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=10)
        features = Feature.objects.order_by('id').all()
        self.user_map.featurestatus_set.collect_features(self.user_map, features, 500)
        self.factory = RequestFactory()
        self.request = self.factory.get(
                '/job/new/0/true/test/NN/PSM/test/SIMPLE/')
        FeatureStatus.objects.clear_treatment_points(self.user_map)
        FeatureStatus.objects.clear_control_points(self.user_map)
        random_set = list(FeatureStatus.objects.order_by('pk').all().values_list('pk', flat=True))
        treatment_set = random_set[0:4]
        #FeatureStatus.objects.filter(pk__in=treatment_set).update(treated=True)
        layer_services.fs_manager.set_treated(self.user_map, treatment_set)
        self.control_set = random_set[4:10]
        #FeatureStatus.objects.filter(pk__in=self.control_set).update(controlled=True)
        layer_services.fs_manager.set_controlled(self.user_map, self.control_set)

    def test_create_job_should_put_one_job_in_the_database(self):
        request = self.request
        request.user = self.user
        view.create_job(request=request,
                        caliper=0,
                        support='true',
                        covariates='forest_cov',
                        estimator='NN',
                        method='PSM',
                        outcome='forest_los',
                        low_outcome_year=2003,
                        high_outcome_year=2007,
                        error_type='SIMPLE')
        self.assertIsInstance(Job.objects.first(), Job)

    def test_create_job_should_put_four_enteries_into_means_table(self):
        request = self.request
        request.user = self.user
        view.create_job(request=request,
                        caliper=0,
                        support='true',
                        covariates='forest_cov,dis_to_cit',
                        estimator='NN',
                        method='PSM',
                        outcome='forest_los',
                        low_outcome_year=2003,
                        high_outcome_year=2007,
                        error_type='SIMPLE')
        self.assertEqual(len(CBSmeans.objects.all()), 4)

    def test_create_job_should_put_four_enteries_into_results_table(self):
        request = self.request
        request.user = self.user
        view.create_job(request=request,
                        caliper=0,
                        support='true',
                        covariates='forest_cov,dis_to_cit',
                        estimator='NN',
                        method='PSM',
                        outcome='forest_cov',
                        low_outcome_year=2003,
                        high_outcome_year=2007,
                        error_type='SIMPLE')
        self.assertEqual(len(Results.objects.all()), 2)

    def test_create_job_should_put_four_enteries_into_resultschart_table(self):
        request = self.request
        request.user = self.user
        view.create_job(request=request,
                        caliper=0,
                        support='true',
                        covariates='forest_cov,dis_to_cit',
                        estimator='NN',
                        method='PSM',
                        outcome='forest_cov',
                        low_outcome_year=2003,
                        high_outcome_year=2007,
                        error_type='SIMPLE')
        self.assertEqual(len(ResultsChart.objects.all()), 4)

    def test_job_process_should_return_Statistical_Matching_Adapter(self):
        job = Job(user=self.user,
                  covariate_variables='forest_cov',
                  outcome_variables='forest_cov')
        abstractfeature = AbstractFeature()
        data = Data(abstractfeature)
        sma = job.process(data)
        self.assertIsInstance(sma, StatisticalMatchingAdapter)

    def test_new_match_should_set_header_in_psm(self):
        job = Job(user=self.user,
                  covariate_variables='ttime_min,slope',
                  outcome_variables='forest_cov')
        abstractfeature = AbstractFeature()
        data = Data(abstractfeature)
        sma = job.process(data)
        self.assertEqual(sma.names, job.covariate_variables.split(','))

    def test_get_matched_should_return_ids(self):
        job = Job(user=self.user,
                  covariate_variables='forest_cov',
                  outcome_variables='forest_cov')
        abstractfeature = AbstractFeature()
        data = Data(abstractfeature)
        sma = job.process(data)
        self.assertTrue(all([(match in self.control_set) for match in sma.matches]))

class MatchingResultsTestCase(TestCase):
    def setUp(self):
        self.treated = Series([1, 1, 0, 0, 0, 1, 0, 0, 1, 0])
        self.matches = Series([2, 3, 7, 9])
        self.outcome = Series([0, 1, 0, 1, 0, 0, 0, 1, 1, 1])
        self.result = MatchingResults(self.outcome, self.treated, self.matches)

    def test_att(self):
        self.assertEqual(self.result.att, -0.25)

    def test_unmatched_treated_mean(self):
        self.assertEqual(self.result.unmatched_treated_mean, 0.5)

    def test_unmatched_control_mean(self):
        self.assertEqual(self.result.unmatched_control_mean, 0.5)

    def test_matched_treated_mean(self):
        self.assertEqual(self.result.matched_treated_mean, 0.5)

    def test_matched_control_mean(self):
        self.assertEqual(self.result.matched_control_mean, 0.75)

    def test_unmatched_se(self):
        self.assertEqual(self.result.unmatched_se, 1.0)

    def test_unmatched_tstat(self):
        self.assertEqual(self.result.unmatched_tstat, 0.0)

    def test_matched_se(self):
        self.assertEqual(self.result.matched_se, 0.35355339059327379)

    def test_matched_tstat(self):
        self.assertEqual(self.result.matched_tstat, -0.70710678118654746)


class DataTestCase(TestCase):
    def setUp(self):
        class TestFeature(AbstractFeature):
            def __init__(self):
                pass

            def treated_ids(self, map_id):
                return [0, 1, 2, 3]

            def controlled_ids(self, map_id):
                return [7, 4, 5, 6]

            def attribute_values(self, covariates, feature_ids):
                return array([[1, 0, 8], [1, 1, 8], [1, 2, 8],
                              [4, 0, 9], [4, 1, 9], [4, 2, 9],
                              [2, 0, 9], [2, 1, 7], [2, 2, 9],
                              [5, 0, 9], [5, 1, 7], [5, 2, 9],
                              [6, 0, 9], [6, 1, 7], [6, 2, 9],
                              [3, 0, 9], [3, 1, 9], [3, 2, 9],
                              [7, 0, 9], [7, 1, 9], [7, 2, 9],
                              [0, 0, 9], [0, 1, 9], [0, 2, 9]])

        self.test_feature = TestFeature()

    def test_retrieve(self):
        data = Data(self.test_feature)
        data.retrieve(user_map=9, outcome='test', covariates=['test1', 'test2'])

    def test_treated_column(self):
        covariates = 'cov1,cov2,cov3'
        data = Data(self.test_feature)
        data.retrieve(9, 'test', covariates)

        self.assertEquals(data.treated_column.tolist(), [1, 1, 1, 1, 0, 0, 0, 0])

    def test_design_matrix(self):
        covariates = 'cov1,cov2,cov3'
        data = Data(self.test_feature)
        data.retrieve(9, 'test', covariates)
        correct_data = DataFrame([[9.0, 9.0, 9.0],
                                  [8.0, 8.0, 8.0],
                                  [9.0, 7.0, 9.0],
                                  [9.0, 9.0, 9.0],
                                  [9.0, 9.0, 9.0],
                                  [9.0, 9.0, 9.0],
                                  [9.0, 7.0, 9.0],
                                  [9.0, 7.0, 9.0]])

        self.assertEqual(data.design_matrix.values.tolist(), correct_data.values.tolist())
        data.retrieve(user_map=9, outcome='test', covariates=covariates)

    def test_covariate_names(self):
        covariates = 'cov1,cov2,cov3'
        data = Data(self.test_feature)
        data.retrieve(9, 'test', covariates)
        self.assertEqual(data.covariate_names, ['cov1', 'cov2', 'cov3'])


class AbstractFeatureTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=5)
        features = Feature.objects.order_by('id').all()
        self.user_map.featurestatus_set.collect_features(self.user_map, features, 500)
        FeatureStatus.objects.clear_treatment_points(self.user_map)
        FeatureStatus.objects.clear_control_points(self.user_map)
        random_set = list(FeatureStatus.objects.order_by('pk').all().values_list('pk', flat=True))
        self.treatment_set = random_set[0:2]
        #FeatureStatus.objects.filter(pk__in=self.treatment_set).update(treated=True)
        layer_services.fs_manager.set_treated(self.user_map, self.treatment_set)
        self.control_set = random_set[2:5]
        layer_services.fs_manager.set_controlled(self.user_map, self.control_set)
        #FeatureStatus.objects.filter(pk__in=self.control_set).update(controlled=True)
        self.abstractfeature = AbstractFeature()

    def test_treated_ids(self):
        self.assertEquals(self.abstractfeature.treated_ids(self.user_map), self.treatment_set)

    def test_controlled_ids(self):
        self.assertEquals(self.abstractfeature.controlled_ids(self.user_map), self.control_set)

    def test_attribute_values(self):
        feature_ids = self.treatment_set
        Feature.objects.filter(pk__in=self.treatment_set)
        self.abstractfeature.attribute_values(covariates=['slope'], feature_ids=feature_ids)

    def test_attribute_names(self):
        self.abstractfeature.attribute_names(covariates=['slope'])


class StatisticalMatchingAdapterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user_map = Map.objects.create(user=self.user)
        self.upload = self.user.upload_set.create(geom_type='geom', encoding='enc')
        data_location = 'uploads/mex_1km_foralex.shp'
        self.upload.upload_features(data_location, slice_stop=20)
        features = Feature.objects.order_by('id').all()
        self.user_map.featurestatus_set.collect_features(self.user_map, features, 500)
        FeatureStatus.objects.clear_treatment_points(self.user_map)
        FeatureStatus.objects.clear_control_points(self.user_map)
        random_set = list(FeatureStatus.objects.order_by('pk').all().values_list('pk', flat=True))
        self.treatment_set = random_set[0:8]
        #FeatureStatus.objects.filter(pk__in=self.treatment_set).update(treated=True)
        layer_services.fs_manager.set_treated(self.user_map, self.treatment_set)
        self.control_set = random_set[8:20]
        #FeatureStatus.objects.filter(pk__in=self.control_set).update(controlled=True)
        layer_services.fs_manager.set_controlled(self.user_map, self.control_set)
        self.abstractfeature = AbstractFeature()

    def test_integration(self):
        sma = StatisticalMatchingAdapter(matching_method='NN', matching_estimator='logit')
        data = Data(self.abstractfeature)
        data.retrieve(user_map=self.user_map, outcome='test', covariates='slope')
        sma.fit(data.treated_column, data.design_matrix, data.covariate_names)
        sma.match()
        sma.balance_statistics()
