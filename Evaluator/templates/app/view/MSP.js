/**
 * @author vagrant
 */

Ext.require(['Ext.ux.form.ItemSelector']);

Ext.define('Evaluator.view.MSP', {
    extend: 'Ext.window.Window',
    alias: 'widget.msp',
    title: 'Select Matched Control Plots',
    height: 470,
    width: 400,

    initComponent: function () {
        var matchingMethods = Ext.create('Ext.data.Store', {
            fields: ['abbr', 'name'],
            data: [
                {"abbr": "PSM", "name": "Propensity Score Matching"},
                {"abbr": "CM", "name": "Covariate Matching"}
            ]
        });

        var matchingEstimator = Ext.create('Ext.data.Store', {
            fields: ['abbr', 'name'],
            data: [
                {"abbr": "NN1", "name": "Nearest Neighbor 1-1"}
            ]
        });

        var matchingEstimator = Ext.create('Ext.data.Store', {
            fields: ['abbr', 'name'],
            data: [
                {"abbr": "NN1", "name": "Nearest Neighbor 1-1"}
            ]
        });

        var selectedCovariates = Ext.create('Ext.data.Store', {
            storeId: 'selectedcovariates',
            fields: ['name'],
            data: []
        });

        Ext.define('Evaluator.model.Covariates', {
            extend: 'Ext.data.Model',
            fields: ['name'],
            proxy: {
                type: 'ajax',
                url: 'layers/covariates',
                reader: {
                    type: 'json'
                }
            }
        });
        Ext.require('Ext.data.Store');
        matchingCovariates = Ext.create('Ext.data.Store', {
            storeId: 'matchingcovariates',
            model: 'Evaluator.model.Covariates',
            autoLoad: true
        });

        var standardErrorMethod = Ext.create('Ext.data.Store', {
            fields: ['abbr', 'name'],
            data: [
                {"abbr": "SE", "name": "Simple Standard Errors"},
                {"abbr": "CL", "name": "Cluster"},
                {"abbr": "BS", "name": "Bootstrap"},
                {"abbr": "AI", "name": "Abadie and Imbens"}
            ]
        });

        var selector = Ext.create('Ext.ux.form.ItemSelector', {
            maxHeight: '200',
            minWidth: '360',
            imagePath: '../static/src/js/ext/examples/ux/css/images/',
            store: Ext.data.StoreManager.lookup('matchingcovariates'),
            displayField: 'name',
            valueField: 'name',
            value: 'name'
        });

        this.dockedItems = [{
            xtype: 'container',
            layout: 'hbox',
            height: 50,
            width: 390,
            items: [{
                xtype: 'fieldset',
                title: 'Select a Matching Method',
                defaultType: 'radiofield',
                frame: 'true',
                margin: '5 5 10 5',
                items: [{
                    xtype: 'combo',
                    store: matchingMethods,
                    queryMode: 'local',
                    displayField: 'name',
                    valueField: 'abbr'
                }]
            }, {
                xtype: 'fieldset',
                title: 'Matching Estimator',
                defaultType: 'radiofield',
                frame: 'true',
                margin: '5 5 10 5',
                items: [{
                    xtype: 'combo',
                    store: matchingEstimator,
                    queryMode: 'local',
                    displayField: 'name',
                    valueField: 'abbr'
                }]
            }]
        }, {
            xtype: 'fieldset',
            title: 'Select Covariates',
            layout: 'fit',
            frame: 'true',
            margin: '5 5 10 5',
            tool: 'help',
            items: [
                {
                    xtype: 'container',

                    layout: 'hbox',
                    items: [
                        //{
                        //	xtype : 'combo',
                        //	store : Ext.data.StoreManager.lookup('matchingcovariates'),
                        //	displayField : 'name',
                        //	valueField : 'name',
                        //	boxLabel : 'Variable',
                        //  listeners : {
                        //        select : function() {
                        //            selectedCovariates.add({name: this.getValue()});
                        //        }
                        //	}
                        //},

                        selector]

                }
            ]
        },
            //{
            //		    xtype : 'gridpanel',
            //		    height : 100,
            //		    columnWidth : 300,
            //		    padding : '0 17 0 17',
            //		    store : Ext.data.StoreManager.lookup('selectedcovariates'),
            //		    columns : [
            //		        { text : 'Covariates', dataIndex : 'name'}
            //		    ]
            //		},
            {
                xtype: 'fieldset',
                title: 'Advanced Options',
                collapsible: true,
                collapsed: true,
                layout: 'anchor',
                frame: 'true',
                margin: '5 5 10 5',
                items: [{
                    xtype: 'checkbox',
                    fieldLabel: 'Caliper',
                    labelAlign: 'top',
                    labelStyle: 'font-weight: bold;',
                    labelSeparator: '',
                    boxLabel: 'Set a caliper',
                    margin: '5 5 10 5'
                }, {
                    html: 'Add Caliper textbox here'
                }, {
                    xtype: 'checkbox',
                    fieldLabel: 'Common Support',
                    labelAlign: 'top',
                    labelStyle: 'font-weight: bold;',
                    labelSeparator: '',
                    boxLabel: 'Enforce Common Support',
                    margin: '5 5 10 5'
                }, {
                    xtype: 'radiogroup',
                    layout: 'anchor',
                    fieldLabel: 'Standard Errors',
                    labelAlign: 'top',
                    labelStyle: 'font-weight: bold;',
                    labelSeparator: '',
                    margin: '5 5 10 5',
                    items: [{
                        xtype: 'combo',
                        store: standardErrorMethod,
                        queryMode: 'local',
                        displayField: 'name',
                        valueField: 'abbr'
                    }]

                }]
            }, {
                xtype: 'fieldset',
                title: '',
                layout: 'hbox',
                frame: 'true',
                margin: '5 5 10 5',
                items: [{
                    xtype: 'button',
                    text: 'Run Matching Algorithm',
                    handler: function () {
                        var covariates = selector.getValue().join(',')
                        var url = '/job/new/0/true/' + covariates + '/NN/PSM/forest_los/SIMPLE'
                        var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
                        myMask.show();
                        Ext.Ajax.request({
                                url: url,
                                method: 'GET',
                                success: function () {
                                    mexico.redraw(true);
                                    myMask.hide();
                                },
                                failure: function () {
                                    myMask.hide();
                                }
                            }
                        );
                    }
                }, {
                    xtype: 'button',
                    text: 'Clear Matched Points',
                    handler: function () {
                        Ext.Ajax.disableCaching = true;
                        var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
                        myMask.show();
                        Ext.Ajax.request({
                                url: '/map/clear/matched',
                                method: 'GET',
                                timeout: 120000,
                                success: function () {
                                    mexico.redraw(true);
                                    myMask.hide();
                                },
                                failure: function () {
                                    myMask.hide();
                                }
                            }
                        );
                    }
                }]
            }];

        this.callParent();
    }
});
