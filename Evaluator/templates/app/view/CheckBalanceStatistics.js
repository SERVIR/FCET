Ext.require('Ext.data.Store');

Ext.define('Evaluator.model.BalanceStatistics', {
    extend: 'Ext.data.Model',
    fields: ['id', 'name', 'sample', 'treated',
        'control', 'bias', 'biasr', 't', 'pt'],
    proxy: {
        type: 'ajax',
        url: '/tables/cbsmeans/',
        reader: {
            type: 'json'
        }
    }
});

Ext.define('Evaluator.model.TestStatistics', {
    extend: 'Ext.data.Model',
    fields: ['sample', 'pseudo_r2',
        'LR_chi2', 'chi2_pvalue', 'mean_bias', 'med_bias'],
    proxy: {
        type: 'ajax',
        url: '/tables/cbstests/',
        reader: {
            type: 'json'
        }
    }
});

var balanceStatistics = Ext.create('Ext.data.Store', {
    storeId: 'testore',
    model: 'Evaluator.model.BalanceStatistics',
    autoLoad: false
});

testStatistics = Ext.create('Ext.data.Store', {
    storeId: 'testStatistics',
    model: 'Evaluator.model.TestStatistics',
    autoLoad: false
});

//Create chart components

//Create functions to handle value rendering for charts
/** Takes a value and formats it as a percentage to two decimal places */
var percent = function (value) { return [parseFloat(value).toFixed(2), '%'].join('')};

var percentage_point_renderer = function (numberDecimals) {
	return function result_percentage_point(value) {
	    return [parseFloat(value).toFixed(numberDecimals)].join('');
	}
};
/** Takes a value and formats it as a decimal with 2 decimal places */
var decimal = function (value) { return parseFloat(value).toFixed(2)};

var tipsRenderer = function (storeItem) {
    this.setTitle(storeItem.get('name') + ':' + storeItem.get('bias'));
};

var seriesRenderer = function (storeItem, item, barAttr, i) {
    var colors = ['blue', 'yellow'];
    barAttr.fill = colors[i % colors.length];
    return barAttr;
};


var balanceStatisticsChartAxes = [{
    title: 'Percent Bias',
    type: 'Numeric',
    position: 'left',
    fields: ['bias'],
    label: {
        renderer: percentage_point_renderer(0)
    },
    grid: true
},
    {
        type: 'Category',
        position: 'bottom',
        fields: ['name'],
        title: 'Covariates'
    }];

var balanceStatisticsChartSeries = [{
    type: 'column',
    axis: 'left',
    style: {
        fillOpacity: 0.8
    },
    highlight: true,
    renderer: seriesRenderer,
    tips: {
        trackMouse: true,
        width: 140,
        height: 28,
        renderer: tipsRenderer
    },
    label: {
        display: 'outside',
        'text-anchor': 'middle',
        field: 'bias',
        renderer: percentage_point_renderer(2),
        orientation: 'horizontal',
        color: '#333'
    },
    xField: 'name',
    yField: 'bias'
}];

var balanceStatisticsChart = {
    xtype: 'chart',
    width: 400,
    maxHeight: 300,
    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    animate: true,
    style: {background: 'white'},
    store: balanceStatistics,
    axes: balanceStatisticsChartAxes,
    series: balanceStatisticsChartSeries
};

//Careful, factoring out a variable like this breaks the ability to load the store correctly
var beforeMatching = {
    xtype: 'fieldset',
    title: 'Before Matching',
    layout: {type: 'hbox', align: 'stretch'},
    defaults: {flex: 1},
    items: [{
        xtype: 'container',
        items: [{
            xtype: 'gridpanel',
            title: 'Percentiles',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{text: 'Sample', dataIndex: 'name'}]
        }]
    }, {
        xtype: 'container',
        items: [{
            xtype: 'gridpanel',
            title: 'Smallest',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{
                text: 'Sample', dataIndex: 'name'
            }]
        }, {
            xtype: 'gridpanel',
            title: 'Largest',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{
                text: 'Sample', dataIndex: 'name'
            }]
        }]
    }, {
        xtype: 'container',
        items: [{
            xtype: 'gridpanel',
            title: 'Moments',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{text: 'Sample', dataIndex: 'name'}]
        }]
    }]
};

var afterMatching = {
    xtype: 'fieldset',
    title: 'After Matching',
    layout: {
        type: 'hbox', align: 'stretch'
    },
    defaults: {flex: 1},
    items: [{
        xtype: 'container',
        items: [{
            xtype: 'gridpanel',
            title: 'Percentiles',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{text: 'Sample', dataIndex: 'name'}]
        }]
    }, {
        xtype: 'container',
        items: [{
            xtype: 'gridpanel',
            title: 'Smallest',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{text: 'Sample', dataIndex: 'name'}]
        }, {
            xtype: 'gridpanel',
            title: 'Largest',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{text: 'Sample', dataIndex: 'name'}]
        }]
    }, {
        xtype: 'container',
        items: [{
            xtype: 'gridpanel',
            title: 'Moments',
            store: Ext.data.StoreManager.lookup('simpsonsStore'),
            columns: [{text: 'Sample', dataIndex: 'name'}]
        }]
    }]
};

//Create Panel components
var balanceStatisticsPanel = {
    xtype: 'gridpanel',
    title: 'Balance Statistics',
    store: Ext.data.StoreManager.lookup('testore'),
    columns: [
        {text: 'Variable', dataIndex: 'name'},
        {text: 'Sample', dataIndex: 'sample', flex: 1},
        {text: 'Treated', dataIndex: 'treated', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'Control', dataIndex: 'control', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: '% Bias', dataIndex: 'bias', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: '% Bias Reduction', dataIndex: 'biasr', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 't', dataIndex: 't', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'p > t', dataIndex: 'pt', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')}
    ]
};
var tipText = function (tip, text) {
    return '<span data-qtip="'+tip+'">'+text+'</span>';
};

var testStatisticsPanel = {
    xtype: 'gridpanel',
    title: 'Balance Statistics',
    store: Ext.data.StoreManager.lookup('testStatistics'),
    columns: [
        {text: 'Sample', dataIndex: 'sample', flex: 1},
        {text: 'Pseudo R-Squared', dataIndex: 'pseudo_r2', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'Likelihood Ratio', dataIndex: 'LR_chi2', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'Likelihood P-Value', dataIndex: 'chi2_pvalue', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'Mean Bias', dataIndex: 'mean_bias', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'Median Bias', dataIndex: 'med_bias', renderer: Ext.util.Format.numberRenderer('0.00')}]
};

//Definitions of pop up windows
Ext.define('Evaluator.view.CBSplot', {
    extend: 'Ext.window.Window',
    alias: 'widget.cbsplot',
    title: 'Check Balance Statistics',
    tools: [
		{
			type: 'refresh',
			qtip: 'Update displayed data',
			handler: function() {balanceStatistics.load()}
		},{
        type: 'help',
        handler: function() {Ext.MessageBox.alert('',
            'This chart displays the percent bias for control points (blue) and matched control points (yellow). ' +
            'Percent bias is the difference between the mean of the control points and treatment points ' +
            'for a given covariate, normalized by the variation in the covariate, and expressed as a percentage.' +
            '<br><br>' +
            '<b>What is a good value for bias?</b><br><br>' +
            'Ideally, most of the matched control biases are between -5 and 5, with 0 being the best.' +
            '<br><br>' +
            '<b>Why are there negative values?</b><br><br>' +
            'A negative bias shows the control group has a higher mean, ' +
            'while a positive bias shows the control group has a lower mean than the treatment group .' +
            '<br><br>' +
            '<b>Why does the bias get worse after matching?</b><br><br>' +
            'Either the covariate is unimportant in predicting where ' +
            'the treatment points are sited or there are no control points ' +
            'that are similar to the treatment points. '
            )}
    }],
    collapseFirst: false,
    width: 800,
    layout: 'fit',
    initComponent: function () {
        // Create data store for chart of menu bias
        balanceStatistics.load();


        this.dockedItems = [{
            //Charts need to be kept in panel to work
            xtype: 'panel',
            items: [{
                title: 'Balance Statistics',
                minHeight: '320',
                layout: {
                    type: 'fit',
                    align: 'stretch'
                },
                defaults: {
                    flex: 1
                },
                items: [{
                    xtype: 'container',
                    maxHeight: 300,
                    layout: {type: 'vbox', align: 'stretch'},
                    defaults: {flex: 1},
                    items: [balanceStatisticsChart]
                }]
            }]
        }];
        this.callParent();
    }
});

Ext.define('Evaluator.view.CBSpanel', {
    extend: 'Ext.window.Window',
    alias: 'widget.cbspanel',
    tools: [{
        type: 'refresh',
        qtip: 'Update displayed data',
        handler: function() {balanceStatistics.load()}
    },{
        type: 'help',
        handler: function() {Ext.MessageBox.alert('',
            'This chart displays the percent bias for control points (blue) and matched control points (yellow). ' +
            'Percent bias is the difference between the mean of the control points and treatment points ' +
            'for a given covariate, normalized by the variation in the covariate, and expressed as a percentage.' +
            '<br><br>' +
            '<b>What is a good value for bias?</b><br><br>' +
            'Ideally, most of the matched control biases are between -5 and 5, with 0 being the best.' +
            '<br><br>' +
            '<b>Why are there negative values?</b><br><br>' +
            'A negative bias shows the control group has a higher mean, ' +
            'while a positive bias shows the control group has a lower mean than the treatment group .' +
            '<br><br>' +
            '<b>Why does the bias get worse after matching?</b><br><br>' +
            'Either the covariate is unimportant in predicting where ' +
            'the treatment points are sited or there are no control points ' +
            'that are similar to the treatment points. '
        )}
    }],
    collapseFirst: false,
    title: 'Check Balance Statistics',
    width: 800,
    layout: 'fit',
    initComponent: function () {
        // Create data store for chart of menu bias
        balanceStatistics.load();

        this.dockedItems = [balanceStatisticsPanel];
        this.callParent();
    }
});

Ext.define('Evaluator.view.CBStests', {
    extend: 'Ext.window.Window',
    alias: 'widget.cbstests',
    tools: [{
        type: 'refresh',
        qtip: 'Update displayed data',
        handler: function() {testStatistics.load()}
    },{
        type: 'help',
        handler: function() {Ext.MessageBox.alert('',
            'This chart displays the percent bias for control points (blue) and matched control points (yellow). ' +
            'Percent bias is the difference between the mean of the control points and treatment points ' +
            'for a given covariate, normalized by the variation in the covariate, and expressed as a percentage.' +
            '<br><br>' +
            '<b>What is a good value for bias?</b><br><br>' +
            'Ideally, most of the matched control biases are between -5 and 5, with 0 being the best.' +
            '<br><br>' +
            '<b>Why are there negative values?</b><br><br>' +
            'A negative bias shows the control group has a higher mean, ' +
            'while a positive bias shows the control group has a lower mean than the treatment group .' +
            '<br><br>' +
            '<b>Why does the bias get worse after matching?</b><br><br>' +
            'Either the covariate is unimportant in predicting where ' +
            'the treatment points are sited or there are no control points ' +
            'that are similar to the treatment points. '
        )}
    }],
    collapseFirst: false,
    title: 'Check Balance Statistics',
    width: 800,
    layout: 'fit',
    initComponent: function () {
        // Create data store for chart of menu bias
        testStatistics.load();

        this.dockedItems = [{
            xtype: 'container',
            maxHeight: '100',
            layout: {type: 'hbox', align: 'stretch'},
            defaults: {flex: 1},
            items: [testStatisticsPanel]
        }];
        this.callParent();
    }
});

Ext.define('Evaluator.view.CBSdistribution', {
    extend: 'Ext.window.Window',
    alias: 'widget.cbsdistribution',
    title: 'Check Balance Statistics',
    width: 800,
    layout: 'fit',
    initComponent: function () {
        // Create data store for chart of menu bias
        balanceStatistics.load();

        this.dockedItems = [{
            title: 'Distribution Before and After Matching',
            layout: {type: 'vbox', align: 'stretch'},
            defaults: {flex: 1},
            items: [beforeMatching, afterMatching]
        }];
        this.callParent();
    }
});

//functions to handle creation of pop up windows
function createBalanceStatisticsPlot() {
    if (!Ext.getCmp('CBSplot')) {
        Ext.create('widget.cbsplot', {
            id: 'CBSplot',
            autoShow: true
        });
    } else {
        Ext.getCmp('CBSplot').close();
    }
}

function createBalanceStatisticsPanel() {
    if (!Ext.getCmp('CBSpanel')) {
        Ext.create('widget.cbspanel', {
            id: 'CBSpanel',
            autoShow: true
        });
    } else {
        Ext.getCmp('CBSpanel').close();
    }
}

function createBalanceStatisticsTests() {
    if (!Ext.getCmp('CBStests')) {
        Ext.create('widget.cbstests', {
            id: 'CBStests',
            autoShow: true
        });
    } else {
        Ext.getCmp('CBStests').close();
    }
}

function createBalanceStatisticsDistribution() {
    if (!Ext.getCmp('CBSdistribution')) {
        Ext.create('widget.cbsdistribution', {
            id: 'CBSdistribution',
            autoShow: true
        });
    } else {
        Ext.getCmp('CBSdistribution').close();
    }
}

//Side bar panel section
Ext.define('Evaluator.view.CheckBalanceStatistics', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.checkbalancestatistics',
    tools: [
		{
			type: 'progress',
			handler: function() {
				if (progressTracker.isAlert("checkbalancestatistics")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["checkbalancestatistics"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.checkBalanceStatistics)}
		}
	],
	modelUpdate: function() {
		if (progressTracker.isComplete('checkbalancestatistics')) {
			this.showCompleted();
		} else if (progressTracker.isAlert('checkbalancestatistics')) {
			this.showAlert();
		} else if (progressTracker.isDefault('checkbalancestatistics')) {
			this.showDefault();
		}
	},
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
    collapseFirst: false,
    listeners: {
    	expand: function() {
            progressTracker.completeCheckBalanceStatistics()
		}
    },
    initComponent: function () {
        progressTracker.register(this);
        this.dockedItems = [
            {
                xtype: 'button',
                text: 'Plot Balance Statistics',
                handler: createBalanceStatisticsPlot
            },
            {
                xtype: 'button',
                text: 'Tabulate Balance Statistics By Covariate',
                handler: createBalanceStatisticsPanel
            },
            {
                xtype: 'button',
                text: 'View Summary Balance Statistics',
                handler: createBalanceStatisticsTests
            }
        ];

        this.callParent();
    }
});
