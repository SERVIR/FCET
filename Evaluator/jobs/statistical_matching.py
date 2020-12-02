# -*- coding: utf-8 -*-
"""
Created on Mon May 18 15:09:03 2015
@author: Alexander
"""

from statsmodels.api import families
from statsmodels.api import GLM
from statsmodels.tools.tools import add_constant
from statsmodels.stats.weightstats import ttest_ind
import pandas as pd
import numpy as np
from scipy.stats import norm, chisqprob
from collections import defaultdict


import sklearn.neighbors as sk

def fit_reg(covariate, treated, weights=pd.Series()):
    treated = add_constant(treated)
    if not weights.any():
        reg = GLM(covariate, treated)
    else:
        reg = GLM(covariate, treated)
    res = reg.fit()
    return res


class Match(object):
    """Perform matching algorithm on input data and return a list of indicies
    corresponding to matches."""

    def __init__(self, match_type='neighbor', match_algorithm='kdtree'):
        self.match_type = match_type
        self.match_algorithm = match_algorithm

    @staticmethod
    def _extract_groups(treated, covariates):
        groups = treated == True
        observation_count = len(groups)
        treated_group, control_group = covariates[groups == 1], covariates[groups == 0]
        return (treated_group, control_group, observation_count)

    def _naive_match(self, treated_group, control_group, observation_count):

        matches = self._make_match_array(treated_group, control_group)

        for match in treated_group.index:
            dist = abs(treated_group[match] - control_group)  # Note this returns a vector/series
            # potential set caliper later
            if dist.min() <= 100:
                matches[match] = dist.argmin()
        return matches

    def _kd_match(self, treated_group, control_group, observation_count):
        tree = sk.KDTree([[x] for x in control_group], leaf_size=1, metric='minkowski', p=2)

        matches = self._make_match_array(treated_group, control_group)

        # for match in treated_group.index:
        #     dist, ind = tree.query(treated_group[match], k=1, breadth_first=True)
        #     matches[match] = control_group.index[ind[0]][0]

        queries = treated_group[treated_group.index]
        dist, ind = tree.query([[x] for x in queries], k=1, breadth_first=True)
        matches[treated_group.index] = control_group.index[[x for x in ind]].values.flatten()
        return matches

    def _make_match_array(self, treated_group, control_group):
        matches = treated_group.append(control_group)
        matches[:] = np.NAN
        return matches

    def match(self, treated, covariates):
        treated_group, control_group, observation_count = self._extract_groups(treated, covariates)
        if self.match_algorithm == 'brute':
            matches = self._naive_match(treated_group, control_group, observation_count)
        elif self.match_algorithm == 'kdtree':
            matches = self._kd_match(treated_group, control_group, observation_count)
        else:
            pass
        return matches


class StatisticalMatching(object):
    """Propensity Score Matching in Python."""

    def __init__(self, method='propensity_score'):
        self.method = method
        self._matches = None
        self.treated = None
        self.design_matrix = None
        self.name = None
        self.pscore = None
        self.att = None
        self.unmatched_treated_mean = None
        self.matched_treated_mean = None
        self.unmatched_control_mean = None
        self.matched_control_mean = None

    def results(self, outcome):
        """
        Recieve outcome variable and return Results object
        :param outcome: A Pandas Series or NumPy array containing outcome values
        :return: Results object
        """

        return Results(outcome=outcome, psm=self)

    def _set_names(self, names):
        """
        Finds a source of names. Intended to be used to apply names to the statistical matching instance
        :param names: List of names provided by user or dataframe
        :return: list of names
        """
        if names:
            return names
        else:
            try:
                names = list(self.design_matrix.columns)
            except AttributeError:
                raise AttributeError('No column names provided and names cannot be inferred from data.')
        return names

    def _create_propensity_scores(self, treated, design_matrix, link_type='logit'):
        if link_type == 'logit':
            link = families.links.logit
        elif link_type == 'probit':
            link = families.links.probit

        family = families.Binomial(link)
        reg = GLM(treated, design_matrix, family=family)
        fitted_reg = reg.fit()
        return fitted_reg

    def fit(self, treated, design_matrix, names=None):
        """Store propensity score and relevant data from propensity score regression"""
        if names:
            design_matrix = pd.DataFrame(design_matrix, columns=names)
        treated = pd.Series(treated)

        self.design_matrix = add_constant(design_matrix)
        self.treated = treated.astype('bool')

        self.fitted_reg = self._create_propensity_scores(self.treated, self.design_matrix)
        self.pscore = self.fitted_reg.fittedvalues
        self.names = self._set_names(names)

    def match(self, match_method='neighbor'):
        """Take fitted propensity scores and match between treatment and
        control groups"""
        # check for valid method
        if self.method == 'propensity_score':
            if match_method == 'neighbor':
                algorithm = Match(match_type='neighbor')
            self._matches = algorithm.match(self.treated, self.pscore)

    @property
    def matches(self):
        return self._matches


class Results(object):
    """
    Class to hold matching results
    """

    def __init__(self, outcome, psm):
        assert isinstance(outcome, pd.Series)
        self.outcome = outcome
        self.treated = psm.treated
        self.matches = psm.matches

    @property
    def ATT(self):
        """
        Computes the Average Treatment Effect on the Treated
        Expressed as: E[Y_{1i} - Y_{0i} | D_{i} = 1]
        Where Y is an outcome variable,
        Y_{1i} and Y_{0i} are values in the treatment and control group,
        and D is dummy of whether treatment was applied
        """
        matches = self.matches
        treatment_index = np.isfinite(matches)
        control_index = np.asarray(self.matches[np.isfinite(matches)], dtype=np.int32)

	#Double check these indicies during testing .... they seem out of order
        match_treatment = self.outcome[treatment_index]
        match_control = self.outcome[control_index]

        return np.mean(np.subtract(match_treatment, match_control))

    @property
    def unmatched_treated_mean(self):
        """
        Calculates the mean of the outcome variable for observation that
        are in the treatment group
        """
        return np.mean(self.outcome[self.treated == 1])

    @property
    def unmatched_control_mean(self):
        """
        Calculates the mean of the outcome variable for observation that
        are not in the treatment group
        """
        return np.mean(self.outcome[self.treated == 0])

    @property
    def matched_treated_mean(self):
        """
        Calculates the mean of the outcome variable for treated observations
        that also have a match
        """
        has_match = np.isfinite(self.matches)
        return np.mean(self.outcome[has_match])

    @property
    def matched_control_mean(self):
        """
        Calculates the mean of the outcome variable for matched observations
        from the control group
        """

        has_match = np.isfinite(self.matches)
        match_index = np.asarray(self.matches[has_match], dtype=np.int32)
        return np.mean(self.outcome[match_index])

    @property
    def unmatched_standard_error(self):
        """
        Calculates standard error of naive treatment effect
        """
        return (self.unmatched_treated_mean - self.unmatched_control_mean) / float(self.unmatched_t_statistic)

    @property
    def unmatched_t_statistic(self):
        """
        Calculate the t-statistics of the unmatched standard error
        """
        treated = self.outcome[self.treated]
        controlled = self.outcome[~self.treated]
        (tstat, _, _) = ttest_ind(treated, controlled)
        return tstat

    @property
    def unmatched_p_value(self):
        """
        Calculate the t-statistics of the unmatched standard error
        """
        treated = self.outcome[self.treated]
        controlled = self.outcome[~self.treated]
        (_, pvalue, _) = ttest_ind(treated, controlled)
        return pvalue

    @property
    def matched_standard_error(self):
        """
        Calculates standard error of matched treatment effect
        """

        def get_average_variance(s1, s2, n1, n2, sum_squared_weights):
            """
            Calculates the average weighted variance of the treatment and control sample
            :param s1: Treatement group variance
            :param s2: Control group variance
            :param n1: Sample size of treatment group
            :param n2: Sample size of control group
            :param sum_squared_weights: Sum squares of control observation wieghts
            :return: Returns average variance as a float
            """
            # Same as s1/float(n2) + (s2*float(sum_squared_weights))/(float(n2)**2)
            return 1 / float(n1) * s1 + float(sum_squared_weights) / (float(n1) ** 2.0) * s2

        def get_match_weights(matches):
            """
            Takes a list of match indicies and counts duplicates to determine weights
            :param matches: Pandas or numpy array representing mathes
            :return: Array of weights
            """
            weights = defaultdict(lambda: 0)
            match_indicies = matches[np.isfinite(matches)]

            for value in match_indicies:
                weights[value] += 1
            return np.asarray(weights.values())

        def sample_variance(outcomes):
            """
            Find the sample variance of a treatment or control sample
            :param outcomes: Outcome values related to a treatment or control group
            :return: Returns sample variance as a float
            """
            # Set degree of freedom as n - 1
            return np.var(outcomes, ddof=1)

        treatment_outcomes = self.outcome[self.treated]

        has_match = np.isfinite(self.matches)
        match_index = np.asarray(self.matches[has_match], dtype=np.int32)
        unique_matches = np.unique(match_index)  # don't repeat weighted obs
        control_outcomes = self.outcome[unique_matches]

        treatment_variance = sample_variance(treatment_outcomes)
        control_variance = sample_variance(control_outcomes)

        n1, n2 = len(treatment_outcomes), len(np.unique(match_index))
        W = np.sum(get_match_weights(self.matches) ** 2)

        average_variance = get_average_variance(treatment_variance, control_variance, n1, n2, W)
        return np.sqrt(average_variance)

    @property
    def matched_t_statistic(self):
        """
        Calculate the t-statistics of the matched standard error
        """
        return (self.matched_treated_mean - self.matched_control_mean) / float(self.matched_standard_error)


class BalanceStatistics(pd.DataFrame):
    """
    Class for balance statistics from a StatisticalMatching instance as a data frame
    """

    def __init__(self, statmatch):
        """
        Populate a pandas data frame and pass it forward as BalanceStatistics. Generally, operations are vectorized
        where possible and each method works on several covariates from a statistical matching routine at a time.
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: BalanceStatistics instance
        """

        # Could be replaced with an ordered dictionary
        columns = ['unmatched_treated_mean',
                   'unmatched_control_mean',
                   'unmatched_bias',
                   'unmatched_t_statistic',
                   'unmatched_p_value',
                   'matched_treated_mean',
                   'matched_control_mean',
                   'matched_bias',
                   'matched_t_statistic',
                   'matched_p_value',
                   'bias_reduction']

        data = {'unmatched_treated_mean': self._unmatched_treated_mean(statmatch),
                'unmatched_control_mean': self._unmatched_control_mean(statmatch),
                'unmatched_bias': self._unmatched_bias(statmatch),
                'unmatched_t_statistic': self._unmatched_t_statistic(statmatch),
                'unmatched_p_value': self._unmatched_p_value(statmatch),
                'matched_treated_mean': self._matched_treated_mean(statmatch),
                'matched_control_mean': self._matched_control_mean(statmatch),
                'matched_bias': self._matched_bias(statmatch),
                'matched_t_statistic': self._matched_t_statistic(statmatch),
                'matched_p_value': self._matched_p_value(statmatch),
                'bias_reduction': self._bias_reduction(statmatch)}

        # dataframe with column defined above
        super(BalanceStatistics, self).__init__(data, index=statmatch.names, columns=columns)

        # Whenever it becomes a problem that we have three copies of how to run regression, we can refactor this into another class
        fitted_reg = self._fit_unmatched_regression(statmatch)
        self.unmatched_prsquared = 1 - fitted_reg.llf / fitted_reg.llnull
        self.unmatched_llr = -2 * (fitted_reg.llnull - fitted_reg.llf)
        self.unmatched_llr_pvalue = chisqprob(self.unmatched_llr, fitted_reg.df_model)

        fitted_reg = self._fit_matched_regression(statmatch)
        self.matched_prsquared = 1 - fitted_reg.llf / fitted_reg.llnull
        self.matched_llr = -2 * (fitted_reg.llnull - fitted_reg.llf)
        self.matched_llr_pvalue = chisqprob(self.matched_llr, fitted_reg.df_model)

    def _unmatched_treated_mean(self, statmatch):
        """
        Compute the unmatched treated mean for every matching variable using vectorized operations
        Expressed as: E[X_{1i}| D_{i} = 1]
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing means for each matching variable
        """
        return np.array(statmatch.design_matrix[statmatch.names][statmatch.treated].mean())

    def _unmatched_control_mean(self, statmatch):
        """
        Compute the unmatched control mean for every matching variable using vectorized operations
        Expressed as: E[X_{1i}| D_{i} = 0]
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing means for each matching variable
        """
        return np.array(statmatch.design_matrix[statmatch.names][~statmatch.treated].mean())

    def _unmatched_bias(self, statmatch):
        """
        Compute the unmatched bias for every matching variable using vectorized operations
        Expressed as: 100 * (m1u - m0u) / sqrt((v1u + v0u) / 2)
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing normalized percent bias for each matching variable
        """
        treated_variance = np.array(statmatch.design_matrix[statmatch.names][statmatch.treated].var())
        control_variance = np.array(statmatch.design_matrix[statmatch.names][~statmatch.treated].var())
        normal = np.sqrt((treated_variance + control_variance) / 2)
        return 100 * (self._unmatched_treated_mean(statmatch) - self._unmatched_control_mean(statmatch)) / normal

    def _unmatched_t_statistic(self, statmatch):
        """
        Compute t-statistics for the difference of means test for every matching variable using vectorized operations
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing t-stats for each matching variable
        """
        treated = np.array(statmatch.design_matrix[statmatch.names][statmatch.treated])
        control = np.array(statmatch.design_matrix[statmatch.names][~statmatch.treated])
        (tstat, _, _) = ttest_ind(treated, control)
        return tstat

    def _unmatched_p_value(self, statmatch):
        """
        Compute p-values for the difference of means test for every matching variable using vectorized operations
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing t-stats for each matching variable
        """
        treated = np.array(statmatch.design_matrix[statmatch.names][statmatch.treated])
        control = np.array(statmatch.design_matrix[statmatch.names][~statmatch.treated])
        (_, pvalue, _) = ttest_ind(treated, control)
        return pvalue

    def _matched_treated_mean(self, statmatch):
        """
        Compute the matched treated mean for every matching variable using vectorized operations
        Expressed as: E[X_{2i}| D_{i} = 1]
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing means for each matching variable
        """
        has_match = np.isfinite(statmatch.matches)
        return np.array(statmatch.design_matrix[statmatch.names][has_match].mean())

    def _matched_control_mean(self, statmatch):
        """
        Compute the matched control mean for every matching variable using vectorized operations
        Expressed as: E[X_{2i}| D_{i} = 0]
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing means for each matching variable
        """
        has_match = np.isfinite(statmatch.matches)
        match_index = np.asarray(statmatch.matches[has_match], dtype=np.int32)

        return np.array(statmatch.design_matrix[statmatch.names].ix[match_index].mean())

    def _matched_bias(self, statmatch):
        """
        Compute the matched bias for every matching variable using vectorized operations
        Expressed as: 100 * (m1m - m0m) / sqrt((v1m + v0m) / 2)
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing normalized percent bias for each matching variable
        """
        treated_variance = np.array(statmatch.design_matrix[statmatch.names][statmatch.treated].var())
        control_variance = np.array(statmatch.design_matrix[statmatch.names][~statmatch.treated].var())

        normal = np.sqrt((treated_variance + control_variance) / 2)

        return 100 * (self._matched_treated_mean(statmatch) - self._matched_control_mean(statmatch)) / normal

    def _matched_t_statistic(self, statmatch):
        """
        Compute t-statistics for the difference of  matched means test for every matching variable
        using vectorized operations
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing t-stats for each matching variable
        """

        def get_match_weights(matches):
            """
            Takes a list of match indicies and counts duplicates to determine weights
            :param matches: Pandas or numpy array representing mathes
            :return: Array of weights
            """
            weights = defaultdict(lambda: 0)
            match_indicies = matches[np.isfinite(matches)]

            for value in match_indicies:
                weights[value] += 1
            return np.asarray(weights.values())

        has_match = np.isfinite(statmatch.matches)
        match_index = np.asarray(statmatch.matches[has_match], dtype=np.int32)
        unique_matches = np.unique(match_index)  # don't repeat weighted obs
        weights = get_match_weights(statmatch.matches)

        treated = np.array(statmatch.design_matrix[statmatch.names][has_match])
        control = np.array(statmatch.design_matrix[statmatch.names].ix[unique_matches])

        (tstat, _, _) = ttest_ind(treated, control, weights=(None, weights))
        return tstat

    def _matched_p_value(self, statmatch):
        """
        Compute p-values for the difference of matched means test for every matching variable
        using vectorized operations
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing t-stats for each matching variable
        """

        def get_match_weights(matches):
            """
            Takes a list of match indicies and counts duplicates to determine weights
            :param matches: Pandas or numpy array representing matches
            :return: Array of weights
            """
            weights = defaultdict(lambda: 0)
            match_indicies = matches[np.isfinite(matches)]

            for value in match_indicies:
                weights[value] += 1
            return np.asarray(weights.values())

        has_match = np.isfinite(statmatch.matches)
        match_index = np.asarray(statmatch.matches[has_match], dtype=np.int32)
        unique_matches = np.unique(match_index)  # don't repeat weighted obs
        weights = get_match_weights(statmatch.matches)

        treated = np.array(statmatch.design_matrix[statmatch.names][has_match])
        control = np.array(statmatch.design_matrix[statmatch.names].ix[unique_matches])

        (_, pvalue, _) = ttest_ind(treated, control, weights=(None, weights))
        return pvalue

    def _bias_reduction(self, statmatch):
        """
        Compute the bias reduced by matching for every matching variable using vectorized operations
        Expressed as: 100*(abs(bias) - abs(biasm))/abs(bias)
        :param statmatch: StatisticalMatching instance that has been fitted
        :return: NumPy array containing t-stats for each matching variable
        """
        biasm = self._matched_bias(statmatch)
        bias = self._unmatched_bias(statmatch)
        return 100 * (abs(bias) - abs(biasm)) / abs(bias)

    def _fit_unmatched_regression(self, statmatch):
        link = families.links.probit
        family = families.Binomial(link)
        reg = GLM(statmatch.treated, statmatch.design_matrix, family=family)
        return reg.fit()

    def _fit_matched_regression(self, statmatch):
        has_match = np.isfinite(statmatch.matches)
        treated_index = has_match[has_match == True].index
        match_index = np.asarray(statmatch.matches[has_match], dtype=np.int32)
        regression_index = treated_index.append(match_index)

        link = families.links.probit
        family = families.Binomial(link)
        reg = GLM(statmatch.treated.ix[regression_index], statmatch.design_matrix.ix[regression_index],
                  family=family)
        return reg.fit()

    @property
    def unmatched_mean_bias(self):
        """
        Compute the matched mean bias of every covariate in check balance statistics
        :return: float
        """

        return self.unmatched_bias.abs().mean()

    @property
    def matched_mean_bias(self):
        """
        Compute the matched mean bias of every covariate in check balance statistics
        :return: float
        """

        return self.matched_bias.abs().mean()

    @property
    def unmatched_median_bias(self):
        """
        Compute the unmatched median bias of every covariate in check balance statistics
        :return: float
        """

        return self.unmatched_bias.abs().median()

    @property
    def matched_median_bias(self):
        """
        Compute the matched median bias of every covariate in check balance statistics
        :return: float
        """

        return self.matched_bias.abs().median()


class RosenbaumBounds(object):
    """
    Computes Rosenbaum bounds for statistical matching with binary outcome, more accurately referred to
    as Mantel-Haenzel bounds.
    Based on:
     Becker, Sascha O. and Caliendo, Marco, Mhbounds - Sensitivity Analysis for Average Treatment Effects (January 2007).
     IZA Discussion Paper No. 2542. Available at SSRN: http://ssrn.com/abstract=958699
    """

    def __init__(self, statmatch):
        self.statmatch = statmatch
        self.treated_size = float
        self.unique_control_size = float
        self.total_observations = float
        self.successes_treated = float
        self.successes = float

    def fit(self, outcome):
        self.treated_size = float(self.statmatch.treated.sum())
        self.unique_control_size = float(self.statmatch.matches.value_counts().count())
        self.total_observations = float(self.treated_size + self.unique_control_size)
        self.successes_treated = float(outcome[self.statmatch.treated == True].sum())
        successes_controlled_unique = outcome.ix[self.statmatch.matches.value_counts().index].sum()
        self.successes = float(self.successes_treated + successes_controlled_unique)

    def q_mh(self, gamma, bound_type):
        EXPECTED_NO_EFFECT = 0.5

        def abs_diff(Y, E):
            return np.abs(Y - E)

        if gamma == 1:
            failures = self.total_observations - self.successes
            hypergeometric_mean = self.treated_size * self.successes / self.total_observations
            hypergeometric_variance = (self.treated_size * self.unique_control_size * self.successes) * (failures) / \
                                      ((self.total_observations ** 2) * (self.total_observations - 1.0))

            q_mh_plus = self._standard_z_score(
                    value=abs_diff(self.successes_treated, hypergeometric_mean),
                    mean=EXPECTED_NO_EFFECT,
                    standard_deviation=np.sqrt(hypergeometric_variance)
            )

        else:
            expected_successes = self._expected_successes(gamma=gamma, bound_type=bound_type, successes=self.successes,
                                                          treated_size=self.treated_size,
                                                          total_observations=self.total_observations)
            if not expected_successes:
                return None

            q_mh_plus = self._standard_z_score(
                    value=abs_diff(self.successes_treated, expected_successes),
                    mean=EXPECTED_NO_EFFECT,
                    standard_deviation=np.sqrt(
                            self._variance_treated_successes(expected_successes, self.successes, self.treated_size,
                                                             self.total_observations))
            )
        return q_mh_plus

    def q_mh_plus(self, gamma):
        """
        Mantel-Haenzel test-statistic for an upper bound on the odds-ratio
        :param gamma: Parameter for the bound, odds-ratio < gamma
        :return: Mantel-Haenzel test-statistic
        """
        return self.q_mh(gamma, bound_type='upper')

    def q_mh_minus(self, gamma):
        """
        Mantel-Haenzel test-statistic for a lower bound on the odds-ratio
        :param gamma: Parameter for the bound, 1/gamma < odds-ratio
        :return: Mantel-Haenzel test-statistic
        """
        return self.q_mh(gamma, bound_type='lower')

    def p_mh_plus(self, gamma):
        qmh = self.q_mh_plus(gamma)
        if qmh:
            return 1-norm.cdf(qmh)
        else:
            return None

    def p_mh_minus(self, gamma):
        qmh = self.q_mh_minus(gamma)
        if qmh:
            return 1-norm.cdf(qmh)
        else:
            return None

    def _expected_successes(self, gamma, bound_type, successes, treated_size, total_observations):
        """
        Returns expected number of successes for a given upper or lower bound on the odds_ratio, gamma, of two
        observations being in the treatment group.
        :param gamma: Odds-ratio bound
        :param bound_type: upper or lower bound of expected successes ['upper', 'lower']
        :param successes: The actual number of successful outcomes in the data
        :param treated_size: The number of observations in treated group in the data
        :param total_observations: The total number of observations in the data
        :return: float
        """

        def quadratic_root(a, b, c):
            """
            Helper function to solve equations of the form a*x**2 + b*x + c = 0
            :param a: First coefficient in a quadratic equation
            :param b: Second coefficient in a quadratic equation
            :param c: Third coefficient in a quadratic equation
            :return: tuple of quadratic roots
            """
            upper = (-b + np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
            lower = (-b - np.sqrt(b ** 2 - 4 * a * c)) / (2 * a)

            return (upper, lower)

        def is_in_support(expected_successes, successes, treated_size, total_observations):
            """
            Determines whether the expected_successes value is within the bound for a Mantel-Haenszel test-statistic
            which is based on a hypergeometric distribution and has the same support function.
            support: k in {max(0, N1 + Y1 - N), min(Y1,N1)}
            :param expected_successes: E
            :param successes: Y1 or K
            :param treated_size: N1 or n
            :param total_observations: N
            :return: True or False
            """
            lower_bound = max(0, successes + treated_size - total_observations)
            upper_bound = min(successes, treated_size)

            return lower_bound < expected_successes < upper_bound

        if bound_type == 'upper':
            odds_ratio_bound = gamma
        elif bound_type == 'lower':
            odds_ratio_bound = 1 / gamma

        a = odds_ratio_bound - 1
        b = -((odds_ratio_bound - 1) * (treated_size + successes) + total_observations)
        c = odds_ratio_bound * successes * treated_size

        upper_guess, lower_guess = quadratic_root(a, b, c)

        if is_in_support(upper_guess, successes, treated_size, total_observations):
            return upper_guess
        elif is_in_support(lower_guess, successes, treated_size, total_observations):
            return lower_guess

    def _variance_treated_successes(self, expected_successes, successes, treated_size, total_observations):
        """
        Calculates the large sample variance approximation of the Mantel-Haenzel test-statistic.
        As stated in Becker and Caliendo, mhbounds - Sensitivity Analysis for Average Treatment Effects, Jan. 2007
        :param expected_successes: E
        :param successes: Y1
        :param treated_size: N1
        :param total_observations: N
        :return: float
        """

        return (
                   (1 / expected_successes) +
                   (1 / (successes - expected_successes)) +
                   (1 / (treated_size - expected_successes)) +
                   (1 / (total_observations - successes - treated_size + expected_successes))
               ) ** -1

    def _standard_z_score(self, value, mean, standard_deviation):
        """
        Standardizes z-score
        :param value: Value of the element in the distribution
        :param mean: Normal distribution mean, mu
        :param standard_deviation: Normal distribution standard deviation, sigma
        :return: z-score
        """
        return (value - mean) / standard_deviation
