from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.shapes import Drawing
import itertools
from math import ceil, floor, log10, copysign


class Formatter(object):
    """
    Base class for formatting objects
    """
    def __init__(self):
        pass

    def _format(self, x):
        """
        Place holder function to determine type of formatting for a column
        """
        return x

    def format_column(self, data, column):
        """
        Iterate over a column in the provided data and apply the given formatting
        function
        """
        return_data = []
        for row in data:
            new_row = row[:column] + [self._format(row[column])] + row[column + 1:]
            return_data.append(new_row)
        return return_data


class DecimalFormatter(Formatter):
    """
    Class to reformat data columns into a fixed number of decimals
    """
    def __init__(self, decimals):
        self.decimals = decimals

    def _format(self, x):
        x = float(x)
        return ("{:."+ str(self.decimals) + "f}").format(x)


class ResultReport(object):
    """
    Collection of helper functions to specify the reporting pdf document
    """
    def __init__(self, file_buffer):
        """Setup the document with paper size and margins """
        self.doc = SimpleDocTemplate(
                file_buffer,
                rightMargin=inch/2,
                leftMargin=inch/2,
                topMargin=inch/2,
                bottomMargin=inch/2,
                pagesize=letter,
        )
        self.elements = []
        self.styles = getSampleStyleSheet()
        self.chart_offset_x = 50
        self.chart_offset_y = 50
        self.chart_height = 125
        self.chart_width = 430

    @staticmethod
    def sanitize_data(data):
        """
        Clean up input data so it can be read by reportlab

        :param data:
        :return:
        """
        # Cast any iterable of an iterable to a list of list
        return [[value for value in row] for row in data]

    @staticmethod
    def sanitize_fields(fields):
        """
        Perform any necessary clean-up of field data for presentation
        """
        fields = fields.copy()
        # Convert list to have proper spacing
        # Note that covariates are currently passed as a string
        fields['covariates'] = ', '.join(fields['covariates'])

        # Make standard error labels human readable
        standard_error_names = {'SIMPLE': 'Simple'}
        fields['standard_errors'] = standard_error_names[fields['standard_errors']]

        # Present True/False as Yes/No
        for key, item in fields.items():
            if item is True:
                fields[key] = 'Yes'
            if item is False:
                fields[key] = 'No'

        return fields

    @staticmethod
    def _calculate_y_axis(data):
        """
        Calculate a reasonable range for y-axis for a given set of data
        """

        data = list(itertools.chain.from_iterable(data)) # flatten list
        tick_count = 5.0
        lower_bound = min(data)
        upper_bound = max(data)
        #axis_range = unrounded_upper_bound - unrounded_lower_bound
        #lower_bound = unrounded_lower_bound - 0.05 * axis_range
        #upper_bound = unrounded_upper_bound + 0.05 * axis_range

        def round_upper(y_max):
            """
            Round yMax to a suitable axis value
            :return:
            """
            greater_than_zero = y_max > 0

            if not greater_than_zero:
                return 0
            elif greater_than_zero:
                return 10**ceil(log10(y_max))

        def round_lower(y_min):
            """
            Round yMin to a suitable axis value
            :param y_min:
            :return:
            """

            less_than_zero = y_min < 0
            if not less_than_zero:
                return 0

            elif less_than_zero:
                return -10**ceil(log10(abs(y_min)))

        #round to best decimal point
        lower_bound = round_lower(lower_bound)
        upper_bound = round_upper(upper_bound)
        tick_size = max([abs(lower_bound), abs(upper_bound)]) / tick_count

        return {'min': lower_bound, 'max': upper_bound, 'step': tick_size}

    def title(self, title):
        self.elements.append(
                Paragraph(title, self.styles['Title'])
        )

    def heading(self, heading):
        self.elements.append(Paragraph(heading, self.styles['Heading2']))

    def subheading(self, subheading):
        self.elements.append(Paragraph(subheading, self.styles['Heading4']))

    def textline(self, textline):
        self.elements.append(Paragraph(textline, self.styles['BodyText']))

    def balance_statistics_chart(self, control_vars, match_vars, var_names):
        """
        Specify layout of the balance statistics chart and generate
        flowable object that can be added to the pdf
        """
        drawing = Drawing()
        vbc = VerticalBarChart()

        # Chart position in document
        vbc.x = self.chart_offset_x
        vbc.y = self.chart_offset_y
        vbc.height = self.chart_height
        vbc.width = self.chart_width

        # Specify data
        # [[control_var1, control_var2], [match_var1, match_var2]]
        vbc.data = [control_vars, match_vars]

        #Set Y-Axis ranges
        #axis_range = self._calculate_y_axis(vbc.data)
        #vbc.valueAxis.valueMin = axis_range['min']
        #vbc.valueAxis.valueMax = axis_range['max']
        #vbc.valueAxis.valueStep = axis_range['step']

        #Grid formatting
        vbc.valueAxis.visibleGrid = 1
        vbc.valueAxis.gridStrokeColor = colors.lightgrey

        #Bar formatting
        vbc.bars[0].fillColor = colors.blue
        vbc.bars[1].fillColor = colors.yellow
        vbc.bars.strokeColor = None
        vbc.groupSpacing = 1
        vbc.barWidth = 5

        # Callout label formatting (numbers above bar)
        #vbc.barLabels.fontName = "Arial"
        vbc.barLabels.fontSize = 8
        vbc.barLabels.fillColor = colors.black
        vbc.barLabelFormat = '%.2f'
        vbc.barLabels.nudge = 5

        # Central axis
        vbc.categoryAxis.visibleTicks = 1

        # X-axis labels
        #vbc.categoryAxis.labels.dy = -60
        vbc.valueAxis.labels.fontName = 'Helvetica'
        vbc.categoryAxis.categoryNames = var_names

        lab = Label()
        lab.setOrigin(10,155)
        lab.boxAnchor = 'ne'
        lab.angle = 90
        lab.dx = 0
        lab.dy = -15

        #lab.boxStrokeColor = colors.green
        lab.setText('Percent Bias')
        drawing.add(lab)
        drawing.add(vbc)
        self.elements.append(drawing)

    def results_chart(self, control_mean, match_mean, treated_mean, att):
        """
        Specify layout of the results chart and generate
        flowable object that can be added to the pdf
        """
        drawing = Drawing()
        vbc = VerticalBarChart()

        # Offset chart from border and text
        vbc.x = self.chart_offset_x
        vbc.y = self.chart_offset_y

        # Set figure size
        vbc.height = self.chart_height
        vbc.width = self.chart_width

        # Specify chart -- list of lists -- list of series with enteries
        vbc.data = [[control_mean, match_mean, treated_mean, att]]

        #Set Y-Axis ranges
        #axis_range = self._calculate_y_axis(vbc.data)
        #vbc.valueAxis.valueMin = axis_range['min']
        #vbc.valueAxis.valueMax = axis_range['max']
        #vbc.valueAxis.valueStep = axis_range['step']

        #Grid formatting
        vbc.valueAxis.visibleGrid = 1
        vbc.valueAxis.gridStrokeColor = colors.lightgrey

        # Set bar characteristics
        vbc.bars[(0,0)].fillColor = colors.blue
        vbc.bars[(0,1)].fillColor = colors.yellow
        vbc.bars[(0,2)].fillColor = colors.red
        vbc.bars[(0,3)].fillColor = colors.green
        vbc.bars.strokeColor = None
        vbc.barSpacing = 2

        # Create callout labels
        #vbc.barLabels.fontName = "Helvetica"
        vbc.barLabels.fontSize = 8
        vbc.barLabels.fillColor = colors.black
        vbc.barLabelFormat = '%.2f'
        vbc.barLabels.nudge = 5

        # X-axis labels
        #vbc.categoryAxis.labels.dy = -60
        #vbc.valueAxis.labels.fontName = 'Helvetica'
        vbc.categoryAxis.categoryNames = ['Control Mean',
                                          'Matched Control Mean',
                                          'Treatment mean',
                                          'ATT']

        lab = Label()
        lab.setOrigin(10,155)
        lab.boxAnchor = 'ne'
        lab.angle = 90
        lab.dx = 0
        lab.dy = -15

        #lab.boxStrokeColor = colors.green
        lab.setText('Result Values')
        drawing.add(lab)

        drawing.add(vbc)
        self.elements.append(drawing)

    def balance_statistics_table(self, data):
        def make_header(text_collection):
            """Add table header styling to text"""
            return [Paragraph(text, self.styles['Heading5'])
                    for text in text_collection]

        # Format table column text, without styling
        dformatter = DecimalFormatter(2)
        data = dformatter.format_column(data, 2)
        data = dformatter.format_column(data, 3)
        data = dformatter.format_column(data, 4)
        data = dformatter.format_column(data, 5)
        data = dformatter.format_column(data, 6)
        data = dformatter.format_column(data, 7)

        #Assemble table
        header =  make_header(['Variable', 'Sample', 'Treated', 'Control',
                               '% Bias', '% Bias Reduction', 'T-Stat', 'p > t'])
        table_data = [header]
        table_data.extend(data)
        table = Table(table_data)

        # Style the table
        table.setStyle(
                TableStyle([
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
        self.elements.append(table)

    def summary_statistics_table(self, data):
        def make_header(text_collection):
            """Add table header styling to text"""
            return [Paragraph(text, self.styles['Heading5']) for text in text_collection]

        # Format table column text, without styling
        dformatter = DecimalFormatter(2)
        data = dformatter.format_column(data, 1)
        data = dformatter.format_column(data, 2)
        data = dformatter.format_column(data, 3)
        data = dformatter.format_column(data, 4)
        data = dformatter.format_column(data, 5)

        #Assemble table
        header =  make_header(['Sample', 'Pseudo R-Squared', 'Likelihood Ratio',
                               'Likelihood P-Value', 'Mean Bias', 'Median Bias'])
        table_data = [header]
        table_data.extend(data)
        table = Table(table_data)

        # Style the table
        table.setStyle(
                TableStyle([
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
        self.elements.append(table)

    def results_table(self, data):
        def make_header(text_collection):
            """Add table header styling to text"""
            return [Paragraph(text, self.styles['Heading5']) for text in text_collection]

        # Format table column text, without styling
        dformatter = DecimalFormatter(2)
        data = dformatter.format_column(data, 2)
        data = dformatter.format_column(data, 3)
        data = dformatter.format_column(data, 4)
        data = dformatter.format_column(data, 5)
        data = dformatter.format_column(data, 6)

        #Assemble table
        header =  make_header(['Variable', 'Sample', 'Treated', 'Controls',
                               'Difference', 'T-Stat', 'Standard Error'])
        table_data = [header]
        table_data.extend(data)
        table = Table(table_data)

        # Style the table
        table.setStyle(
                TableStyle([
                    ('ALIGN', (0,0), (0,0), 'LEFT'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
        self.elements.append(table)

    def page_break(self):
        self.elements.append(PageBreak())

    def build(self):
        self.doc.build(self.elements)

def generate_results_report(target_file, fields):
    report = ResultReport(file_buffer=target_file)
    fields = report.sanitize_fields(fields)

    report.title('Forest Conservation Evaluation Tool Results'.format(**fields))
    report.heading('Date of Study')
    report.textline('Study started on: {session_start_time}'.format(**fields))
    report.textline('Report generated on: {report_generated_time}'.format(**fields))
    report.heading('Define Study Area')
    report.textline('Selected Regions: {country}'.format(**fields))

    report.heading('Define Outcome Period')
    report.textline('Start year: {start_year}'.format(**fields))
    report.textline('End year: {end_year}'.format(**fields))

    report.heading('Limit Plot Types')
    report.textline('Minimum forest cover: {min_forest_cover}%'.format(**fields))
    report.textline('Maximum forest cover: {max_forest_cover}%'.format(**fields))
    report.textline('')
    #report.subheading('Land use types included')
    #report.textline('')
    #report.textline('Agroforest: {agroforest}'.format(**fields))
    #report.textline('Agriculture: {agriculture}'.format(**fields))
    #report.textline('Forest: {forest}'.format(**fields))

    report.heading('Select Treatment Areas')
    report.textline('Option used: {treatment_area_option}'.format(**fields))

    report.heading('Select Control Areas')
    report.textline('Option used: {control_area_option}'.format(**fields))

    report.heading('Select Matched Control Plots')
    report.textline('Matching method: {matching_method}'.format(**fields))
    report.textline('Matching estimator: {matching_estimator}'.format(**fields))
    report.textline('Covariates: {covariates}'.format(**fields))
    #report.subheading('Advanced setting'.format(**fields))
    #report.textline('Caliper: {caliper}'.format(**fields))
    #report.textline('Common support: {common_support}'.format(**fields))
    #report.textline('Standard errors: {standard_errors}'.format(**fields))

    report.page_break()

    report.textline('<strong>FIGURE 1:</strong> Study area with red (policy), yellow (matched control), and blue (unmatched control) points'.format(**fields))
    report.textline(' '.format(**fields))
    report.textline(' '.format(**fields))
    report.elements.append(Image(fields['map_url']))

    report.page_break()
    report.heading('Check Balance Statistics')
    report.textline('<strong>FIGURE 2:</strong> Plot of balance statistics'.format(**fields))
    report.balance_statistics_chart(fields['balance_statistics_means_unmatched'],
                                    fields['balance_statistics_means_matched'],
                                    fields['balance_statistics_var_names'])

    report.page_break()
    report.textline('<strong>TABLE 1.</strong> Table of balance statistics'.format(**fields))
    report.textline('<br></br>')
    report.balance_statistics_table(report.sanitize_data(fields['balance_statistics_data']))
    report.textline('<br></br>')
    report.textline('<strong>TABLE 2.</strong> Table of summary balance statistics'.format(**fields))
    report.textline('<br></br>')
    report.summary_statistics_table(report.sanitize_data(fields['summary_statistics_data']))

    report.page_break()
    report.heading('Results')
    report.textline('<strong>FIGURE 3:</strong> Plot of results'.format(**fields))

    report.results_chart(
            control_mean=fields['control_mean'],
            match_mean=fields['match_mean'],
            treated_mean=fields['treated_mean'],
            att=fields['att'])

    report.textline('<strong>TABLE 3.</strong> Table of results'.format(**fields))
    report.textline('<br></br>')
    report.results_table(data=report.sanitize_data(fields['results_data']))

    #report.heading('Check Sensitivity')
    #report.textline('<strong>TABLE 4.</strong> Table of Rosenbaum bounds'.format(**fields))
    # Write to filestream
    report.build()
