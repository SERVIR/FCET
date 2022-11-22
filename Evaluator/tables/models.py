"""
Models used to hold data for tables display on the front end.
ExtJS has its own set of models which mirror these directly
"""

from django.db import models
from jobs.models import Job
import numpy as np


# In it's current state these models could be condensed to a view, but
# they are here for future data persistence, which may be condensed as well

class CBSmeansManager(models.Manager):
    """Helper class for means table"""

    def create_table(self, job, balance_statistics):
        """
        Populates balance statistic means in database
        """
        for name in balance_statistics.index:
            try:
                means = CBSmeans(job=job,
								 name=name,
								 sample='Unmatched',
								 treated=balance_statistics.unmatched_treated_mean[name],
								 control=balance_statistics.unmatched_control_mean[name],
								 bias=balance_statistics.unmatched_bias[name],
								 biasr=balance_statistics.bias_reduction[name],
								 t=balance_statistics.unmatched_t_statistic[name],
								 pt=balance_statistics.unmatched_p_value[name])
                means.save()
            except:
                raise Exception("Could not write {} to tables. Values passed: {}".format(
					name, 
					(means.name, means.sample, means.treated, means.control, means.bias, means.biasr, means.t, means.pt))
				)

            try:
                means = CBSmeans(job=job,
								 name=name,
								 sample='Matched',
								 treated=balance_statistics.matched_treated_mean[name],
								 control=balance_statistics.matched_control_mean[name],
								 bias=balance_statistics.matched_bias[name],
								 biasr=balance_statistics.bias_reduction[name],
								 t=balance_statistics.matched_t_statistic[name],
								 pt=balance_statistics.matched_p_value[name])
                means.save()
            except:
                raise Exception("Could not write {} to tables. Values passed: {}".format(
					name, 
					(means.name, means.sample, means.treated, means.control, means.bias, means.biasr, means.t, means.pt))
				)

    def get_table(self, user_map):
        """
        Retrieves balance statistic means from databse
        """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].cbsmeans_set.order_by('pk').all()
        else:
            return []

    def get_table_as_list(self, user_map):
        """
        Retrieves data for balance statistics table from database as list
        """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].cbsmeans_set.order_by('pk').all() \
                .values_list('name', 'sample', 'treated', 'control', 'bias', 'biasr', 't', 'pt')
        else:
            return []

class CBSmeans(models.Model):
    """
    Models data for Check Balance Statistics table of means
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default='')
    sample = models.CharField(max_length=100, blank=True, default='')
    treated = models.DecimalField(max_digits=18, decimal_places=10, blank=True, null=True)
    control = models.DecimalField(max_digits=18, decimal_places=10, blank=True, null=True)
    bias = models.DecimalField(max_digits=11, decimal_places=5, blank=True, null=True)
    biasr = models.DecimalField(max_digits=11, decimal_places=5, blank=True, null=True)
    t = models.DecimalField(max_digits=11, decimal_places=5, blank=True, null=True)
    pt = models.DecimalField(max_digits=11, decimal_places=5, blank=True, null=True)
    objects = CBSmeansManager()


class CBStestsManager(models.Manager):
    """Helper class for table of test of balance statistics"""

    def create_table(self, job, balance_statistics):
        tests = CBStests(job=job,
                         sample='Unmatched',
                         pseudo_r2=balance_statistics.unmatched_prsquared,
                         LR_chi2=balance_statistics.unmatched_llr,
                         chi2_pvalue=balance_statistics.unmatched_llr_pvalue,
                         mean_bias=balance_statistics.unmatched_mean_bias,
                         med_bias=balance_statistics.unmatched_median_bias)
        tests.save()
        tests = CBStests(job=job,
                         sample='Matched',
                         pseudo_r2=balance_statistics.matched_prsquared,
                         LR_chi2=balance_statistics.matched_llr,
                         chi2_pvalue=balance_statistics.matched_llr_pvalue,
                         mean_bias=balance_statistics.matched_mean_bias,
                         med_bias=balance_statistics.matched_median_bias)
        tests.save()

    def get_table(self, user_map):
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].cbstests_set.order_by('pk').all()
        else:
            return []

    def get_table_as_list(self, user_map):
        """
        Retrieves data for results table from database as list
        """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].cbstests_set.order_by('pk').all() \
                .values_list('sample', 'pseudo_r2', 'LR_chi2', 'chi2_pvalue', 'mean_bias', 'med_bias')
        else:
            return []

class CBStests(models.Model):
    """
    Models data for Check Balance Statistics test statistic table
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    sample = models.CharField(max_length=100, blank=True, default='')
    pseudo_r2 = models.FloatField()
    LR_chi2 = models.FloatField()
    chi2_pvalue = models.FloatField()
    mean_bias = models.FloatField()
    med_bias = models.FloatField()
    objects = CBStestsManager()


class ResultsManager(models.Manager):
    """Helper class for table of results"""

    def create_table(self, job, results, outcome_name):
        """
        Populates data for results table into databse
        """
        means = Results(variable=outcome_name, job=job, sample='Unmatched',
                        treated=results.unmatched_treated_mean,
                        controls=results.unmatched_control_mean,
                        difference=results.unmatched_treated_mean - results.unmatched_control_mean,
                        standard_error=results.unmatched_standard_error,
                        t_stat=results.unmatched_t_statistic)
        means.save()

        means = Results(variable='', job=job, sample='ATT',
                        treated=results.matched_treated_mean,
                        controls=results.matched_control_mean,
                        difference=results.matched_treated_mean - results.matched_control_mean,
                        standard_error=results.matched_standard_error,
                        t_stat=results.matched_t_statistic)
        means.save()

    def get_table(self, user_map):
        """
        Retrieves data for results table from database
        """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].results_set.order_by('pk').all()
        else:
            return []

    def get_table_as_list(self, user_map):
        """
        Retrieves data for results table from database as list
        """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].results_set.order_by('pk').all() \
                .values_list('variable', 'sample', 'treated', 'controls', 'difference', 't_stat', 'standard_error')
        else:
            return []


# TODO: Do we want to connect CBStests and Results based on sample?
class Results(models.Model):
    """
    Models data that is fed into the results tables
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    variable = models.CharField(max_length=100, blank=True, default='')
    sample = models.CharField(max_length=100, blank=True, default='')
    treated = models.FloatField()
    controls = models.FloatField()
    difference = models.FloatField()
    standard_error = models.FloatField()
    t_stat = models.FloatField()
    objects = ResultsManager()


class CheckSensitivityManager(models.Manager):
    """Helper class for table Mantel-Hanzel sensitivity measures"""

    def create_table(self, job, bounds):
        for gamma in range(1, 100):
            bound_statistics = CheckSensitivity(
                    job=job,
                    gamma=gamma / float(10),
                    q_plus=bounds.q_mh_plus(gamma / float(10)),
                    q_minus=bounds.q_mh_minus(gamma / float(10)),
                    p_plus=bounds.p_mh_plus(gamma / float(10)),
                    p_minus=bounds.p_mh_minus(gamma / float(10))
            )
            bound_statistics.save()

    def get_table(self, user_map):
        """
         Retrieves data for checksensitivity table from database
         """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].checksensitivity_set.order_by('pk').all()
        else:
            return []


class CheckSensitivity(models.Model):
    """
    Models data that is fed into the Check Sensitivity table
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    gamma = models.DecimalField(max_digits=3, decimal_places=1)
    q_plus = models.FloatField(null=True)
    q_minus = models.FloatField(null=True)
    p_plus = models.FloatField(null=True)
    p_minus = models.FloatField(null=True)
    objects = CheckSensitivityManager()


class ResultsChartManager(models.Manager):
    """Helper class for table of results"""

    def create_table(self, job, results, outcome_name):
        """
        Populates results chart data from psm object
        """
        value = ResultsChart(job=job,
                             name='Unmatched Control',
                             data_values=results.unmatched_control_mean)
        value.save()
        value = ResultsChart(job=job,
                             name='Matched Control',
                             data_values=results.matched_control_mean)
        value.save()
        value = ResultsChart(job=job,
                             name='Treatment',
                             data_values=results.matched_treated_mean)
        value.save()
        value = ResultsChart(job=job,
                             name='ATT',
                             data_values=results.matched_treated_mean - results.matched_control_mean)
        value.save()

    def get_table(self, user_map):
        """
        Retrieves most recent job results for a given user
        """
        job = Job.objects.most_recent(user_map)
        if job:
            # Order is not guaranteed without order_by
            return job[0].resultschart_set.order_by('pk').all()
        else:
            return []


class ResultsChart(models.Model):
    """
    Models data that is fed to the front end results chart
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, default='')
    data_values = models.FloatField()
    objects = ResultsChartManager()
