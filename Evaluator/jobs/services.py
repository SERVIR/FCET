from layers.models import AttributeValue, Attribute
import layers.services as layer_services
from pandas import DataFrame, Index, Series
from .statistical_matching import StatisticalMatching, BalanceStatistics, RosenbaumBounds
from itertools import product as cartesian_product
from django.core.cache import cache

class StatisticalMatchingAdapter(object):
    def __init__(self, matching_method, matching_estimator):
        self.matching_method = matching_method
        self.matching_estimator = matching_estimator
        self.stat_match = StatisticalMatching()

    def fit(self, treated_column, design_matrix, covariate_names):
        self.stat_match.fit(treated=treated_column, design_matrix=design_matrix, names=covariate_names)

    def match(self):
        self.stat_match.match()

    def results(self, outcome):
        return self.stat_match.results(outcome)

    def balance_statistics(self):
        return BalanceStatistics(self.stat_match)

    def bounds(self, outcome):
        bounds = RosenbaumBounds(self.stat_match)
        bounds.fit(outcome)
        return bounds

    @property
    def names(self):
        return self.stat_match.names

    @property
    def matches(self):
        return self.stat_match.matches.dropna()


class Data(object):
    """
    Class to shape incoming feature data into data suitable for statistical matching
    """

    def __init__(self, abstractfeature):
        self.abstractfeature = abstractfeature

    def retrieve(self, user_map, outcome, covariates):
        self.outcome = outcome
        self.covariates = covariates
        self.user_map = user_map
        self.treated_ids = self.abstractfeature.treated_ids(self.user_map)
        self.controlled_ids = self.abstractfeature.controlled_ids(self.user_map)
        self.index = Index(self.treated_ids + self.controlled_ids)
        self._outcome = Series()
        self._design_matrix = DataFrame()
        # Remove rows that don't pass quality check
        new_index = self._check_data(self.design_matrix)
        assert (len(self.index) - len(new_index)) < 10000, "Dropped too many rows while preparing data"
        self.index = new_index

    def _check_data(self, data):
        # I can see this being refactored into its own class if we
        # create an interface for adding data constraints
        data_filter = Series(True, index=self.index)

        if 'ttim_mn' in data.columns:
            data_filter = data_filter & data.ttim_mn.ge(0)

        if 'aspect' in data.columns:
            data_filter = data_filter & data.aspect.ge(0)

        if 'dem' in data.columns:
            data_filter = data_filter & data.dem.ge(0)

        if 'pdensty' in data.columns:
            data_filter = data_filter & data.pdensty.ge(0)

        return data.index[data_filter]

    @property
    def treated_column(self):
        treated_features = Series(True, index=self.treated_ids)
        controlled_features = Series(False, index=self.controlled_ids)

        # Check for empty input
        if treated_features.empty:
            raise ValueError('Treated feature list is empty')

        if controlled_features.empty:
            raise ValueError('Controlled feature list is empty')
        treated = treated_features.append(controlled_features)

        return treated.reindex(self.index)

    @property
    def design_matrix(self):
        if self._design_matrix.empty:
            feature_ids = self.treated_ids + self.controlled_ids
            attributes = self.abstractfeature.attribute_values(self.covariate_names, feature_ids)
            self._design_matrix = self._query_to_dataframe(attributes, self.covariate_names)
            # Slightly messy error handling if the attribute table is not properly constructed
            assert len(self.covariate_names) == self._design_matrix.shape[1], "The number of returned covariates does not match the number of requested covariates."
            self._design_matrix.dropna(axis=1, how='all', 
                    thresh=0.1*self._design_matrix.shape[0], inplace=True)
            self._design_matrix.rename(columns=self.abstractfeature.attribute_names(self.covariate_names), inplace=True)

        self._design_matrix = self._design_matrix.reindex(self.index)
        return self._design_matrix

    @property
    def covariate_names(self):
        return self.covariates.split(',')

    def outcome_column(self, low_deforestation_year, high_deforestation_year):
        if self._outcome.empty:
            feature_ids = self.treated_ids + self.controlled_ids
            outcome = self.abstractfeature.attribute_values(self.outcome_names, feature_ids)
            outcome = self._query_to_dataframe(outcome, self.outcome_names)
            self._outcome = outcome
            self._outcome.rename(columns=self.abstractfeature.attribute_names(self.outcome_names), inplace=True)
            self._outcome = self._outcome[self.outcome_names[0]]

        self._outcome = self._outcome.reindex(self.index)

        # Line to modify how the deforestation column is coded either as 1-12 or 2001 - 2012
        # The app expects 2001-2012
        outcome = self._outcome + 2000

        return self._is_deforested(outcome, low_deforestation_year, high_deforestation_year)

    @property
    def outcome_names(self):
        outcome_name = self.outcome.split(',')
        assert len(outcome_name) == 1
        return outcome_name

    def _is_deforested(self, outcome_column, low_query_year, high_query_year):
        """
        Computes boolean column of whether a given outcome was in effect after a certain year

        :param outcome_column: Integer-like column of years that state when an outcome occurred in a geospatial location
        :param query_year: Year in which we determine whether the outcome was in effect or not
        :return:
        """

        low_query_year = int(low_query_year)
        high_query_year = int(high_query_year)
        in_lower_bound = outcome_column >= low_query_year
        in_upper_bound = high_query_year >= outcome_column
        return in_lower_bound & in_upper_bound

    def _query_to_dataframe(self, attributes, covariates):
        records = DataFrame.from_records(attributes, columns=['feature_id', 'attribute_name', 'value'])
        records = records.convert_objects(convert_numeric=True)
        records['value'] = records.value.apply(float)
        records = records.pivot(index='feature_id', columns='attribute_name', values='value')

        return records


class AbstractFeature(object):
    """
    Class to decouple the abstract notion of features vs the actual feature type

    We want statistical matching to work regardless of whether we use polygons, points, multipoints, etc
    """

    def __init__(self):
        pass

    def treated_ids(self, user_map):
        return layer_services.get_treatment_points(user_map)

    def controlled_ids(self, user_map):
        return layer_services.get_control_points(user_map)

    def attribute_values(self, covariates, feature_ids):
        """
        Retrieve values associated with every attribute value pair.

        The list of attribute ids will be longer than necessary because it may contain attributes for
        regions that we do not query in. These additional attributes will be eliminated because the
        corresponding features are not in the feature_ids list.
        """

        attribute_dict = self.attribute_names(covariates)
        attribute_ids = attribute_dict.keys()
        values = AttributeValue.objects.attribute_values(attribute_ids, feature_ids)
        # We return attribute names instead of IDs to be able to work across shapefiles 
        # This matches the convention that the user experiences
        values = [(fid, attribute_dict.get(aid), v) for fid, aid, v in values]
        return values

    def attribute_names(self, covariates):
        """
        Retrieve all attributes (columns) whose name is in the covariates list.

        This will retrieve more ids than necessary because attributes can belong to different
        countries or shapefile uploads and share the same name.
        """
        attribute_ids = Attribute.objects.filter(name__in=covariates)
        return {attribute.id: attribute.name for attribute in attribute_ids}
