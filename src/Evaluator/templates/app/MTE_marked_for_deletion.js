/**
 * @author vagrant
 */

//Define models and ajax requests
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
var testStore = Ext.create('Ext.data.Store', {
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
var result_percent = function (value, metadata, record) {
    return [parseFloat(value  * 100).toFixed(2), '%'].join('');
}

var percentage_point_renderer = function (numberDecimals) {
	return function result_percentage_point(value, metadata, record) {
	    return [parseFloat(value  * 100).toFixed(numberDecimals)].join('');
	}
}

var resultSeriesRenderer = function (storeItem, item, barAttr, i, store) {
    var colors = ['blue', 'yellow', 'red', 'green'];
    barAttr.fill = colors[i % colors.length];
    return barAttr;
}

var resultTipsRenderer = function (storeItem, item) {
    this.setTitle(storeItem.get('name') + ':' + storeItem.get('data_values'));
}

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
    }]

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
    }]

var resultsPanel = 
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
                                afterrender : function(chart, opts) {
                                    this.store.load()
                                }
                            },
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
				testDock = this.dockedItems;
				this.callParent();
				
			}
		});
