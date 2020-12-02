# -*- coding: utf-8 -*-
"""
Created on Mon May 18 15:09:03 2015
@author: Alexander
"""

from os import environ
environ['MPLCONFIGDIR'] = '/tmp/'
from statsmodels.api import families
from statsmodels.api import GLM
import pandas as pd
import numpy as np
from pickle import dump
from collections import defaultdict
from sklearn.neighbors import KDTree
import logging
logger = logging.getLogger(__name__)

#Consider extracting a results class

def fit_reg(covariate,treated, weights=pd.Series()):
    link = families.links.logit
    family = families.Binomial(link)
    if not weights.any():
        reg = GLM(covariate, treated,family=family, sigma=weights)
    else:
        reg = GLM(covariate, treated,family=family)
    res = reg.fit()
    return res

class Match(object):
    """Perform matching algorithm on input data and return a list of indicies
    corresponding to matches."""
    def __init__(self, match_type='neighbor', match_algorithm='brute'):
        self.match_type = match_type
        self.match_algorithm = match_algorithm

    @staticmethod
    def _extract_groups(treated, covariates):
        groups = treated == treated.unique()[0]
        n = len(groups)
        n1 = groups.sum()
        n2 = n-n1
        g1, g2 = covariates[groups == 1], covariates[groups == 0]
        return (g1, g2, n)

    @staticmethod
    def _naive_match(g1, g2, n):
        matches = pd.Series(np.empty(n))
        matches[:] = np.NAN

        for m in g1.index:
            # Note this returns a vector/series
            dist = abs(g1[m]-g2)
            #potential set caliper later
            if dist.min() <= 100:
                matches[m] = dist.argmin()

        return matches
        
    @staticmethod
    def _kd_match(g1, g2, n):
        logger.debug("Began matching")
        matches = pd.Series(np.empty(n))
        matches[:] = np.NAN
        index = g1.index
        g2_index = g2.index
        g1 = np.array([[x] for x in g1])
        g2 = np.array([[x] for x in g2])
        kd = KDTree(g2)        
        
        for m in index:
                _, matches[m] = kd.query(g1[m], k=1)
                matches[m] = g2_index[matches[m]-1]
        logger.debug("Finished matching")
        return matches

    def match(self, treated, covariates):
        g1, g2, n = self._extract_groups(treated, covariates)
        if self.match_algorithm == 'brute':
            matches = self._kd_match(g1, g2, n)
        else:
            pass
        return matches

class PropensityScoreMatching(object):
    """Propensity Score Matching in Python."""
    def __init__(self, model='logit'):
        self.model = model
        self._matches = None
        self.treated = None
        self.design_matrix = None
        self.header = None
        self.pscore = None
        self.att = None
        self.unmatched_treated_mean = None
        self.matched_treated_mean = None
        self.unmatched_control_mean = None
        self.matched_control_mean = None
        self.ids = None
    
    def _compute_att(self, outcome):
        """
        Computes the Average Treatment Effect on the Treated
        
        Expressed as: E[Y_{1i} - Y_{0i} | D_{i} = 1]
        Where Y is an outcome variable,
        Y_{1i} and Y_{0i} are values in the treatment and control group,
        and D is dummy of whether treatment was applied
        """
        matches = np.asarray(self._matches)
        treatment_index = np.isfinite(matches)

        control_index = self._matches[np.isfinite(matches)]
        
        match_treatment = outcome[treatment_index]
        match_control = outcome[control_index]

        return np.mean(np.subtract(match_treatment, match_control))
        
    def results(self, outcome):
        #Outcome transformation should happen outside PSM in original data processing
        outcome = np.asarray(outcome).flatten()
        outcome = np.where(outcome > 0, 1, 0)
        
        treatment = np.asarray(self.treated) == 1
        control = np.asarray(self.treated) == 0
        matches = np.asarray(self._matches)
        match_values = matches[np.isfinite(matches)]
        treatment_index = np.isfinite(matches)
        control_index = self._matches[np.isfinite(matches)]
        match_treatment = outcome[treatment_index]
        match_control = outcome[control_index]

        self.att = self._compute_att(outcome)

        self.unmatched_treated_mean = np.mean(outcome[treatment])
        self.unmatched_control_mean = np.mean(outcome[control])
        self.matched_treated_mean = np.mean(match_treatment)
        self.matched_control_mean = np.mean(match_control)
        
        res = fit_reg(outcome, self.treated)
        self.unmatched_se = res.bse[0]
        self.unmatched_tstat = (self.unmatched_treated_mean - self.unmatched_control_mean) / self.unmatched_se
        
        s1, s2 = np.var(outcome[treatment]), np.var(outcome[control])   
        n1, n2 = len(outcome[treatment]), len(outcome[control])
        n1, n2 = float(n1), float(n2)
        weights = defaultdict(lambda: 0)
       
        for value in match_values:
            weights[value] += 1
        self._weights = np.asarray(weights.values())
        W = np.sum(self._weights**2)
        self.matched_se = np.sqrt(s1/n1 + (s2*W)/(n1**2))
        self.matched_tstat = (self.matched_treated_mean - self.matched_control_mean) / self.matched_se
    
    def compute_balance_means(self, col):
        """
        Compute the means of a given attribute 
        for treated, unmatched, and matched groups
        """
        return {'treated': col[self.treated == 1].mean(),
                'unmatched': col[self.treated == 0].mean(),
                'matched': col.iloc[self._matches.dropna()].mean()}
                
    def compute_balance_variances(self, col):
        """
        Compute the variance of a given attribute 
        for treated, unmatched, and matched groups
        """
        return {'treated': col[self.treated == 1].var(),
                'unmatched': col[self.treated == 0].var(),
                'matched': col.iloc[self._matches.dropna()].var()}
                
    def compute_balance_t_stats(self, col):
        """
        Compute the t-statistics of a given attribute 
        when testing for difference of means between treated/untreated and
        treated/matched control
        """
        return {'unmatched': fit_reg(self.treated, col).tvalues.values[0],
                'matched': fit_reg(self.treated, col, 
                                   weights=self._weights).tvalues.values[0]}
    def compute_balance_p_values(self, col):
        """
        Compute the p-value of of t-tests
        when testing for difference of means between treated/untreated and
        treated/matched control
        """
        return {'unmatched': fit_reg(self.treated, col).pvalues.values[0],
                'matched': fit_reg(self.treated, col, 
                                   weights=self._weights).pvalues.values[0]}

    def compute_balance_statistics(self):
        """Compute balance statistics and return as nested dictionary"""
        all_vars = {}
        
        #Iterate by column in DataFrame
        for index, label in enumerate(self.header):
            all_vars[label] = {}
            #Retrieve column from DataFrame            
            col = self.design_matrix.iloc[:,index]
            
            means = self.compute_balance_means(col)
            all_vars[label]['means'] = means
            
            variances = self.compute_balance_variances(col)
            all_vars[label]['variances'] = variances
            
            t_stats = self.compute_balance_t_stats(col)
            all_vars[label]['t_stats'] = t_stats
            
            p_values = self.compute_balance_p_values(col)
            all_vars[label]['p_values'] = p_values
            
        return all_vars
        
    def fit(self, treated, design_matrix, design_matrix_header):
        """Run logit or probit and set treated, design_matrix, and pscore"""
        #Convert to pandas data structures        
        treated = pd.Series(treated)
        design_matrix = pd.DataFrame(design_matrix)
        #Fit propensity socre
        link = families.links.logit
        family = families.Binomial(link)
        reg = GLM(treated, design_matrix, family=family)
        fitted_reg = reg.fit()
        pscore = fitted_reg.fittedvalues
        #Store values for later refernce
        self.header = design_matrix_header
        self.treated = treated
        self.design_matrix = design_matrix
        self.pscore = pscore

    def match(self, match_method='neighbor'):
        """Take fitted propensity scores and match between treatment and
        control groups"""
        #check for valid method
        if match_method == 'neighbor':
            algorithm = Match(match_type='neighbor')
        self._matches = algorithm.match(self.treated, self.pscore)
        
        matches = np.asarray(self._matches)
        match_values = matches[np.isfinite(matches)]
        
        weights = defaultdict(lambda: 0)
       
        for value in match_values:
            weights[value] += 1
        self._weights = np.asarray(weights.values())

    def get_matches(self):
        return self._matches
    
    def get_matched(self):
        return [self.ids[int(i)] for i in self._matches[np.isfinite(self._matches)]]
        
    def cache(self, filename):
        with open(filename, 'w') as f:
            dump(self, f)    


class MatchingResults(object):
    """Calculates results from a statistical matching procedure"""
    def __init__(self, outcome, treated, matches):
        self.outcome = np.asarray(outcome)
        self.treated = np.asarray(treated)
        self.matches = np.asarray(matches)
        
    @property
    def att(self):
        """
        Computes the Average Treatment Effect on the Treated
        
        Expressed as: E[Y_{1i} - Y_{0i} | D_{i} = 1]
        Where Y is an outcome variable,
        Y_{1i} and Y_{0i} are values in the treatment and control group,
        and D is dummy of whether treatment was applied
        """
        #matches = np.asarray(self.matches)
        matches = self.matches
        treatment_index = np.isfinite(matches)

        control_index = self.matches[np.isfinite(matches)]
        
        match_treatment = self.outcome[treatment_index]
        match_control = self.outcome[control_index]
        
        return np.mean(np.subtract(match_treatment, match_control))
    
    @property
    def unmatched_treated_mean(self):
        """
        Calculates the mean of the outcome variable for observation that
        are in the treatment group
        """
        return np.mean(self.outcome[self.treated==1])

    @property
    def unmatched_control_mean(self):
        """
        Calculates the mean of the outcome variable for observation that 
        are not in the treatment group
        """
        return np.mean(self.outcome[self.treated==0])
    
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
        match_index = self.matches[has_match]
        return np.mean(self.outcome[match_index])

    @property
    def unmatched_se(self):
        """
        Calculates standard error of naive treatment effect
        """
        res = fit_reg(self.outcome, self.treated)
        return res.bse[0]
        
        
    @property
    def unmatched_tstat(self):
        """
        Calculates t-statistic of naive treatment effect
        """
        return (self.unmatched_treated_mean - self.unmatched_control_mean) / self.unmatched_se

    @property
    def matched_se(self):
        """
        Calculates standard error of matched treatment effect
        """
        def get_average_variance(s1, s2, n1, n2, sum_squared_weights):
            return s1/float(n1) + (s2*sum_squared_weights)/(float(n1)**2)
            
        def get_match_weights(matches):
            weights = defaultdict(lambda: 0)
            match_indicies = matches[np.isfinite(matches)]
            
            for value in match_indicies:
                weights[value] += 1
            return np.asarray(weights.values())
            
        treatment_outcomes = self.outcome[self.treated==1]
        control_outcomes = self.outcome[self.treated==0]
        
        treatment_variance = np.var(treatment_outcomes)   
        control_variance = np.var(control_outcomes)        
        n1, n2 = len(treatment_outcomes), len(control_outcomes)

        W = np.sum( get_match_weights(self.matches) ** 2 )

        average_variance = get_average_variance(
            treatment_variance, control_variance, n1, n2, W)
            
        return np.sqrt(average_variance)

    @property
    def matched_tstat(self):
        """
        Calculates t-statistic of matched treatment effect
        """
        return (float(self.matched_treated_mean) - float(self.matched_control_mean)) / float(self.matched_se)

class MahalanobisMatching(object):
    """Mahalanobis matching in Python."""
    def __init__(self):
        pass
