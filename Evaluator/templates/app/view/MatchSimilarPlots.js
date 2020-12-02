//Ext.define("Evaluator.model.CovariateSelection", {
//    extend: 'Ext.data.model',
//    fields: ['name']
//});
//
//selectedCovariates = Ext.create('Ext.data.Store', {
//    storeId: 'selectedcovariates',
//    fields: ['name'],
//    model: "Evaluator.model.CovariateSelection",
//    proxy: {
//        type: 'memory',
//        reader: { type:'json'}
//    }
//});

Ext.define('Evaluator.view.selectCovariates', {
    extend: 'Ext.window.Window',
    alias: 'widget.selectcovariates',
    tools: [{
        type: 'help',
        handler: function() {Ext.MessageBox.alert('',
            'Here you can select covariates/attributes that the matching algorithm will use ' +
            'to gauge similarity between treatment points and control points<br><br>' +
            '<b>What makes a good covariate?</b><br><br>' +
            'An ideal covariate is simultaneously a predictor of the deforestation rate and ' +
            'a characteristic that differs between treatment areas and control areas.<br><br>' +
            'Select all relevant covariates, but do not include ones that do not affect deforestation' +
            ' in the areas or do not vary between treatment points and control points.')}
    }],
    collapseFirst: false,
    title: 'Select Covariates',
    height: 300,
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

        Ext.define('Evaluator.model.Covariates', {
            extend: 'Ext.data.Model',
            fields: ['name', 'display_name'],
            proxy: {
                type: 'ajax',
                url: 'layers/covariates',
                reader: {
                    type: 'json'
                }
            }
        });
        Ext.require('Ext.data.Store');
        var matchingCovariates = Ext.create('Ext.data.Store', {
            storeId: 'matchingcovariates',
            model: 'Evaluator.model.Covariates',
            autoLoad: true
        });
        var selector = Ext.create('Ext.ux.form.ItemSelector', {
            minHeight: '225',
            maxHeight: '225',
            minWidth: '360',
            imagePath: '../static/src/js/ext/examples/ux/css/images/',
            store: Ext.data.StoreManager.lookup('matchingcovariates'),
            displayField: 'display_name',
            valueField: 'name',
            value: [""],
            listeners: {
                boxready: function(covariateSelector) {
                    covariateSelector.setValue(Job.covariates);
                },
                change: function(covariateSelector) {
                    Job.covariates = covariateSelector.getValue();
                }
            }
        });

        this.dockedItems = [
//{
//            xtype: 'container',
//            layout: 'hbox',
//            height: 50,
//            width: 390,
//            items: [{
//                xtype: 'fieldset',
//                title: 'Select a Matching Method',
//                defaultType: 'radiofield',
//                frame: 'true',
//                margin: '5 5 10 5',
//                items: [{
//                    xtype: 'combo',
//                    store: matchingMethods,
//                    queryMode: 'local',
//                    displayField: 'name',
//                    valueField: 'abbr',
//                    value: 'PSM',
//                    listeners: {
//                        select: function(combo, record) {
//                            Job.matchingMethod = combo.getValue();
//                        }
//                    }
//                }]
//            }, 
//		{
//                xtype: 'fieldset',
//                title: 'Matching Estimator',
//                defaultType: 'radiofield',
//                frame: 'true',
//                margin: '5 5 10 5',
//                items: [{
//                    xtype: 'combo',
//                    store: matchingEstimator,
//                    queryMode: 'local',
//                    displayField: 'name',
//                    valueField: 'abbr',
//                    value: 'NN',
//                    listeners: {
//                        select: function(combo, record) {
//                            Job.matchingEstimator = combo.getValue();
//                        }
//                    }
//                }]
//            }]
//        }, 
	{
            xtype: 'fieldset',
            title: 'Select Covariates',
            layout: 'fit',
            frame: 'true',
            margin: '5 5 0 5',
            items: [{
                xtype: 'container',
                layout: 'hbox',
                items: [selector]
            }]
        },{
            xtype: 'button',
            text: 'Submit Selection',
            tooltip: "Don't forget to run the match in the main menu",
            handler: function() {Ext.getCmp('selectCovariates').close()}
        }
        ];

        this.callParent();
    }
});

//Ext.define('Evaluator.view.advancedSettings', {
//    extend: 'Ext.window.Window',
//    alias: 'widget.advancedsettings',
//    title: 'Advanced Settings',
//    width: 400,
//
//    initComponent: function () {
//        var standardErrorMethod = Ext.create('Ext.data.Store', {
//            fields: ['abbr', 'name'],
//            data: [
//                {"abbr": "SE", "name": "Simple Standard Errors"},
//                {"abbr": "CL", "name": "Cluster"},
//                {"abbr": "BS", "name": "Bootstrap"},
//                {"abbr": "AI", "name": "Abadie and Imbens"}
//            ]
//        });
//
//        this.dockedItems = [{
//					xtype: 'fieldset',
//					items: [{
//                    xtype: 'checkbox',
//                    fieldLabel: 'Caliper',
//                    labelAlign: 'top',
//                    labelStyle: 'font-weight: bold;',
//                    labelSeparator: '',
//                    boxLabel: 'Set a caliper',
//                    margin: '5 5 10 5'
//                }]},{
//					xtype: 'fieldset',
//					items: [{
//                    xtype: 'checkbox',
//                    fieldLabel: 'Common Support',
//                    labelAlign: 'top',
//                    labelStyle: 'font-weight: bold;',
//                    labelSeparator: '',
//                    boxLabel: 'Enforce Common Support',
//                    margin: '5 5 10 5'
//                }]
//				} , {
//					xtype: 'fieldset',
//					items: [{
//                    xtype: 'radiogroup',
//                    layout: 'anchor',
//                    fieldLabel: 'Standard Errors',
//                    labelAlign: 'top',
//                    labelStyle: 'font-weight: bold;',
//                    labelSeparator: '',
//                    margin: '5 5 10 5',
//                    items: [{
//                        xtype: 'combo',
//                        store: standardErrorMethod,
//                        queryMode: 'local',
//                        displayField: 'name',
//                        valueField: 'abbr'
//                    }]
//                }]
//				}];
//
//        this.callParent();
//    }
//});

function createSelectCovariatesWindow() {
    if (!Ext.getCmp('selectCovariates')) {
        Ext.create('widget.selectcovariates', {
            id: 'selectCovariates',
            autoShow: true
        });
    } else {
        Ext.getCmp('selectCovariates').close();
    }
}

//function createAdvancedSettingsWindow() {
//    if (!Ext.getCmp('advancedSettings')) {
//        Ext.create('widget.advancedsettings', {
//            id: 'advancedSettings',
//            autoShow: true
//        });
//    } else {
//        Ext.getCmp('advancedSettings').close();
//    }
//}

Ext.define('Evaluator.view.MatchSimilarPlots', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.matchsimilarplots',
    tools: [
		{
			type: 'progress',
			handler: function() {
				if (progressTracker.isAlert("selectmatchedcontrolpoints")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["selectmatchedcontrolpoints"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.selectMatchedControlPoints)}
		}
	],
    collapseFirst: false,
	modelUpdate: function() {
		if (progressTracker.isComplete('selectmatchedcontrolpoints')) {
			this.showCompleted();
		} else if (progressTracker.isAlert('selectmatchedcontrolpoints')) {
			this.showAlert();
		} else if (progressTracker.isDefault('selectmatchedcontrolpoints')) {
			this.showDefault();
		}
	},
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
    listeners: {
		collapse: function() {
			if (progressTracker.isDefault('selectmatchedcontrolpoints')) {
				progressTracker.alert("selectmatchedcontrolpoints", "Don't forget to run the match.");
			} 
		}
    },
    initComponent: function () {
		progressTracker.register(this);
		this.dockedItems = [
            {
                xtype: 'button',
                text: 'Select Covariates',
		handler: createSelectCovariatesWindow
            },
            //{
            //    xtype: 'button',
            //    text: 'Advanced Settings',
				//handler: createAdvancedSettingsWindow
            //},
            {
                xtype: 'button',
                text: 'Run Statistical Matching',
                cls: 'btn-success',
                handler: function () {
					if (!progressTracker.isComplete("definestudyarea") &&
						!progressTracker.isComplete("defineoutcomeperiod") &&
						!progressTracker.isComplete("limitpointtypes") &&
						!progressTracker.isComplete("selecttreatmentpoints") &&
						!progressTracker.isComplete("selecttreatmentpoints")) {
						progressTracker.alert("selectmatchedcontrolpoints", "Please complete all the previous steps before running the match.");
					}

					var progressIcon = this.up().down('tool');
                    var url = '/job/new/'
                    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
                    myMask.show();
                    Ext.Ajax.request({
                            url: url,
                            method: 'POST',
                            timeout: 120000,
                            jsonData: {
                                caliper: 0,
                                support: 'false',
                                covariates: Job.covariates.join(','),
                                estimator: Job.matchingEstimator,
                                method: Job.matchingMethod,
                                outcome: Job.outcome,
                                low_outcome_year: Job.lowOutcomeYear,
                                high_outcome_year: Job.highOutcomeYear,
                                error_type: 'SIMPLE',
                                country: Job.country.join("; "),
                                region_type: Job.regionType,
                                state: Job.state,
                                min_forest_cover: Job.minForestCover,
                                max_forest_cover: Job.maxForestCover,
                                agroforest: 'Yes',
                                agriculture: 'Yes',
                                forest: 'Yes',
                                treatment_area_option: Job.treatmentAreaOption,
                                control_area_option: Job.controlAreaOption,
                                user_start_time: Job.userStartTime
                            },
                            success: function () {
                                mexico.redraw(true);
                                myMask.hide();
								progressTracker.completeSelectMatchedControlPoints();
                            },
                            failure: function () {
                                mexico.redraw(true);
                                myMask.hide();
                            }
                        }
                    );
                }
            },
            {
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
            }];
		
        this.callParent();
    }
});
