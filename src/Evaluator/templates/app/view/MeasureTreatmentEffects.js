Ext.define('Evaluator.model.MTEresult', {
    extend : 'Ext.data.Model',
    fields : ['id', 'variable', 'sample', 'treated', 
                'controls', 'difference', 't_stat', 'standard_error'],
    proxy : {
        type : 'ajax',
        url : 'tables/results',
        reader : {
            type : 'json',
            idProperty : 'id'
        }
    }						
    });
						
Ext.define('Evaluator.model.MTEchart', {
    extend : 'Ext.data.Model',
    fields : ['id', 'name', 'data_values'],
    proxy : {
        type : 'ajax',
        url : 'tables/resultschart',
        reader : {
            type : 'json',
            idProperty : 'id'
        }
    }						
    });

//Define data stores						
Ext.require('Ext.data.Store');					
Ext.create('Ext.data.Store', {
		storeId : 'resultsstore',
		model : 'Evaluator.model.MTEresult',
		autoLoad : false
	});

var resultsChartStore = Ext.create('Ext.data.Store', {
		storeId : 'chartstore',
		model : 'Evaluator.model.MTEchart',
		autoLoad : false
	});

//Define renderers

var result_percent = function (value) {
    return [parseFloat(value  * 100).toFixed(2), '%'].join('');
};

var percentage_point_renderer = function (numberDecimals) {
	return function result_percentage_point(value) {
	    return [parseFloat(value  * 100).toFixed(numberDecimals)].join('');
	}
};

var resultSeriesRenderer = function (storeItem, item, barAttr, i) {
    var colors = ['blue', 'yellow', 'red', 'green'];
    barAttr.fill = colors[i % colors.length];
    return barAttr;
};

var resultTipsRenderer = function (storeItem) {
    this.setTitle(storeItem.get('name') + ':' + storeItem.get('data_values'));
};

var resultsChartAxes = [{
        title : 'Result Values',
        type : 'Numeric',
        position : 'left',
        fields : ['data_values'],
        minimum: '-0.20',
        maximum: '0.20',
        label: {
            renderer: percentage_point_renderer(0)
        },
        grid: true
    },
    {
        type: 'Category',
        position: 'bottom',
        fields: ['name'],
        title: 'Means'
    }];

var resultsChartSeries = [{
    type: 'column',
    axis: 'left',
    style: {
        fillOpacity: 0.8
    },
    highlight: true,
    renderer: resultSeriesRenderer,
    tips: {
        trackMouse: true,
        width: 140,
	    height: 28,
        renderer: resultTipsRenderer
    },
    label: {
        display: 'outside',
        'text-anchor': 'top',
        field: 'data_values',
        renderer: percentage_point_renderer(2),
        orientation: 'horizontal',
	    color: '#333'
    },
    xField: 'name',
    yField: 'data_values'
    }];

Ext.define('Evaluator.view.MTE', {
			extend : 'Ext.window.Window',
			alias : 'widget.mte',
			title : 'Results',
			height : 425,
			width : 700,
			initComponent : function() {
				this.dockedItems = [{
						   xtype : 'chart',
						   width : 500,
						   height : 300,
                           animate : true,
                           style : {background: 'white'},
						   store : resultsChartStore,
						   axes : resultsChartAxes,
	    				   series : resultsChartSeries,
	    				   listeners: {
                                afterrender : function() {
                                    this.store.load()
                                }
                            }
                		}, {
							xtype : 'gridpanel',
							title : 'Results',
							layout: 'fit',
							store : Ext.data.StoreManager.lookup('resultsstore'),
							columns : [
							    {text : 'Variable', dataIndex : 'variable'},
                                {text : 'Sample', dataIndex :'sample'},
                                {text : 'Treated', dataIndex :'treated', renderer: Ext.util.Format.numberRenderer('0.00')},
                                {text : 'Controls', dataIndex :'controls', renderer: Ext.util.Format.numberRenderer('0.00')},
                                {text : 'Difference', dataIndex :'difference', renderer: Ext.util.Format.numberRenderer('0.00')},
                                {text : 'T-Stat', dataIndex :'t_stat', renderer : Ext.util.Format.numberRenderer('0.00')},
                                {text : 'Standard Error', dataIndex :'standard_error', renderer: Ext.util.Format.numberRenderer('0.00')}
                            ],
                            listeners: {
                                afterrender : function() {
                                    this.store.load();
                                }
                            }
	    				}];
				this.callParent();
				
			}
		});
function createResultsPlot() {
    if (!Ext.getCmp('MTEwindow')) {
        Ext.create('widget.mte', {
            id: 'MTEwindow',
            autoShow: true
        });
    } else {
        Ext.getCmp('MTEwindow').close();
    }
}
//function createResultsPanel() {
//    if (!Ext.getCmp('MTEwindow')) {
//        Ext.create('widget.mte', {
//            id: 'MTEwindow',
//            autoShow: true
//        });
//    } else {
//        Ext.getCmp('MTEwindow').close();
//    }
//}

Ext.define('Evaluator.view.MeasureTreatmentEffects', {
			extend : 'Ext.panel.Panel',
			alias : 'widget.measuretreatmenteffects',
			tools: [
				{
					type: 'progress',
					handler: function() {
						if (progressTracker.isAlert("results")) {
							Ext.MessageBox.alert("", progressTracker.completionAlerts["results"])
						}
					}
				},
				{
					type: 'help',
					handler: function() {Ext.MessageBox.alert('', panelDescriptions.results)}
				}
			],
			collapseFirst: false,
			modelUpdate: function() {
				if (progressTracker.isComplete('results')) {
					this.showCompleted();
				} else if (progressTracker.isAlert('results')) {
					this.showAlert();
				} else if (progressTracker.isDefault('results')) {
					this.showDefault();
				}
			},
			showCompleted: function() {this.down('tool').setUI('check')},
			showAlert: function() {this.down('tool').setUI('alert')},
			showDefault: function() {this.down('tool').setUI('default')},
		        listeners: {
			    expand: function() {
			        progressTracker.completeResults()
    				}
   		        },
			initComponent : function() {
			        progressTracker.register(this);
				this.dockedItems = [{
					xtype: 'button',
					text: 'View Results',
					handler: createResultsPlot
				}];
				
				this.callParent();
			}
		});
