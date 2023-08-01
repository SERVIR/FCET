var howToButton = {
	text: '<div style="color: white; font-size: 14px">How To</div>', id: 'howToItem',
	menu: [
	{
		text: 'Description', id: 'descriptionItem',
		listeners: {
			'click': function () {
				var windowObjectReference = window.open('/static/fcet_description.pdf', "FCET Description");
			}
		}
	}, {
		text: 'Instructions', id: 'instructionsItem',
		listeners: {
			'click': function () {
				var windowObjectReference = window.open('/static/fcet_instructions.pdf', "FCET Instructions");
			}
		}
	}, {
		text: 'FAQ', id: 'faqItem',
		listeners: {
			'click': function () {
			}
		}
	}, {
		text: 'Video Tutorial', id: 'videoTutorialItem',
		listeners: {
			'click': function () {
                              var windowObjectReference = window.open('/static/fcet_video-tutorial.pdf', "FCET Video Tutorial");
			}
		}
	}, {
		text: 'User Questions', id: 'userQuestionsItem',
		listeners: {
			'click': function () {
			}
		}
	}, {
		text: 'Email', id: 'emailItem',
		listeners: {
			'click': function () {
				window.location.href = "mailto:fc-evaluation-tool@rff.org";
			}
		}
	}],
		listeners: {
			mouseover: function () {
				this.showMenu();
			},
			menutriggerout: function () {
				//this.hideMenu();
			}
		}
};

var aboutButton = {
    text: '<div style="color: white; font-size: 14px">About</div>', id: 'aboutItem',
    menu: [{
        text: 'Metadata', id: 'metadataItem',
        listeners: {
            'click': function () {
                    var windowObjectReference = window.open('/static/fcet_metadata.pdf', "FCET Metadata");
            }
        }
    }, {
        text: 'Sponsors', id: 'sponsorsItem',
        listeners: {
            'click': function () {
                    var windowObjectReference = window.open('/static/fcet_sponsors.pdf', "FCET Sponsors");
            }
        }
    }, {
        text: 'Team', id: 'teamItem',
        listeners: {
            'click': function () {
                    var windowObjectReference = window.open('/static/fcet_team.pdf', "FCET Team");
            }
        }
    }, {
        text: 'Email', id: 'emailItem2',
        listeners: {
            'click': function () {
                window.location.href = "mailto:fc-evaluation-too@rff.org";
            }
        }
    }],
    listeners: {
        mouseover: function () {
            this.showMenu();
        },
        menutriggerout: function () {
            //this.hideMenu();
        }
    }
};

var feedbackButton = {
    text: '<div style="color: white; font-size: 14px">Feedback</div>', id: 'feedbackItem',
    menu: [{
        text: 'User Questions', id: 'userQuestionsItem2',
        listeners: {
            'click': function () {
            }
        }
    }, {
        id: 'userCommentsItem',
        text: 'User Comments',
        listeners: {
            'click': function () {
            }
        }
    }, {
        text: 'Email', id: 'emailItem3',
        listeners: {
            'click': function () {
                window.location.href = "mailto:fc-evaluation-tool@rff.org";
            }
        }
    }],
    listeners: {
        mouseover: function () {
            this.showMenu();
        },
        menutriggerout: function () {
            //this.hideMenu();
        }
    }
};


var loginForm = Ext.create('Ext.form.Panel', {
    // Any configuration items here will be automatically passed along to
    // the Ext.form.Basic instance when it gets created.

    // The form will submit an AJAX request to this URL when submitted
    url: '/map/login/',

    items: [{
        xtype: 'textfield',
        fieldLabel: 'User Name',
        name: 'username'
    },
        {
            xtype: 'textfield',
            fieldLabel: 'Password',
            inputType: 'password',
            name: 'password'
        }]
/*
    buttons: [{
        text: 'Login',
        handler: function () {
            // The getForm() method returns the Ext.form.Basic instance:
            var form = this.up('form').getForm();
            var win = this.up('window');
            if (form.isValid()) {
                // Submit the Ajax request and handle the response
                form.submit({
                    success: function (form, action) {
                        Ext.Msg.alert('Login Succesful', action.result.message);
                        win.getEl().toggle();
                    },
                    failure: function (form, action) {
                        Ext.Msg.alert('Failed', action.result ? action.result.message : 'Authentication Failed');
                    }
                });
            }
        }
    }]
*/
});
/*
Ext.define('Evaluator.view.LoginWindow',{
	extend: 'Ext.window.Window',
    alias: 'widget.loginwindow',
	title: 'Login',
	autoShow: true,
	width: 250,
	height: 110,
	closable: false,
    layout: 'fit',
    initComponent: function () {
        this.dockedItems = [loginForm];
        this.callParent();
    }

});
*/
Ext.define('Evaluator.view.Viewport', {
    extend: 'Ext.container.Viewport',
    layout: 'fit',
    requires: ['Evaluator.view.MainMap',
        //'Evaluator.view.MTE', 
        'Evaluator.view.CS',
        'Evaluator.view.Overview',
        'Evaluator.view.DefineStudyYears',
        'Evaluator.view.DefineStudyArea',
        'Evaluator.view.LimitPlotTypes',
        'Evaluator.view.SelectPolicyAreas',
        'Evaluator.view.SelectControlAreas',
        'Evaluator.view.MatchSimilarPlots',
        'Evaluator.view.CheckBalanceStatistics',
        'Evaluator.view.MeasureTreatmentEffects',
        'Evaluator.view.CheckSensitivity',
        'Evaluator.view.Report'],
    listeners: {
    	afterrender: function() {
			/*
            if (!Ext.getCmp('LoginWindow')) {
				Ext.create('widget.loginwindow', {
					id: 'LoginWindow',
					autoShow: true
				});
			} else {
				Ext.getCmp('LoginWindow').getEl().toggle();
			}
           */
    	}
    },
    initComponent: function () {
        this.items = {
            dockedItems: [{
                dock: 'top',
                xtype: 'toolbar',
                height: 40,
                layout: 'hbox',
                style: {
                    background: "#4682B4"
                },
				items: [new Ext.Button(howToButton),
				new Ext.Button(aboutButton),
				new Ext.Button(feedbackButton), 
				{
					text: '<div style="color: white; font-size: 14px">Log In</div>',
					handler: function() {
						if (!Ext.getCmp('LoginWindow')) {
							Ext.create('widget.loginwindow', {
								id: 'LoginWindow',
								autoShow: true
							});
						} else {
							Ext.getCmp('LoginWindow').getEl().toggle();
						}
					}
				}, {
					xtype: 'tbspacer',
					width: 50
				}, {
					xtype: 'tbtext',
					height: '39',
					width: '800',
					text: '<div style="color: white; font: bold 22.8571px arial">Forest Conservation Evaluation Tool (Beta)</div>'
				}, {
					xtype: 'tbspacer',
					width: 50
				},  {
					xtype: 'component',
					height: 40,
					width: 120,
					html: '<img height="40" src="/static/SESYNC_transparent_small.png"></img>'
				}, {
					xtype: 'component',
					height: 40,
					width: 50,
					html: '<img height="40" src="/static/nasa-logo.gif"></img>'
				}, {
					xtype: 'component',
					height: 40,
					width: 110,
					html: '<img height="40" src="/static/Mesoamerica2.png"></img>'
				}, {
					xtype: 'component',
					height: 40,
					width: 110,
					html: '<img height="40" src="/static/rff_transparent.gif"></img>'
				}]
            }],
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [
                {
                    width: 260,
                    xtype: 'panel',
                    id: 'west-region',
					autoScroll: true,
                    layout: {
                        type: 'anchor',
                        align: 'stretch'
                    },
                    dockedItems: [{
                        xtype: 'button',
                        text: 'Reset All',
                        height: 40,
                        dock: 'bottom',
                        handler: function () {
                            var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
                            myMask.show();
                            administrativeSelectionLayer.removeAllFeatures();
                            var resetButton = this;
                            progressTracker.setAllIncomplete();
                            Ext.Ajax.request({
                                url: '/map/settings/reset',
                                method: 'GET',
                                success: function () {
                                    map.moveTo(new OpenLayers.LonLat(-95,20).transform('EPSG:4326', 'EPSG:3857'));
                                    map.zoomTo(5);
                                    Job.lowOutcomeYear = 2001;
                                    Job.highOutcomeYear = 2012;
				    Job.covariates = [];
                                    resetButton.up().down("#year-slider").setValue([2001,2012]);
                                    resetButton.up().down("#year-slider-low-label").setText(2001);
                                    resetButton.up().down("#year-slider-high-label").setText(2012);
                                    resetButton.up().down("#forest-slider").setValue([1,100]);
                                    resetButton.up().down("#forest-slider-min-label").setText(0);
                                    resetButton.up().down("#forest-slider-max-label").setText(100);
				    adminFeatureControl.unselectAll();
                                    mexico.redraw(true);
                                    myMask.hide();
                                },
                                failure: function () {
                                    mexico.redraw(true);
                                    myMask.hide();
                                }
                            });
                        }
                    }],
                    items: [{
                        xtype: 'overview',
                        title: 'Overview',
                        collapsible: false,
                        collapsed: true
                    },{
                        xtype: 'definestudyarea',
                        id: 'definestudyarea',
                        title: '1. Define Study Area',
                        collapsible: true,
                        collapsed: true,
                        listeners: {
                            expand:	function() {
                                this.up().down('selectpolicyareas').collapse();
                                this.up().down('selectcontrolareas').collapse();
                                Job.country = [];
                                administrativeLayer.setVisibility(true);
                                administrativeSelectionLayer.setVisibility(true);
                                adminFeatureControl.activate();
                            },
                            collapse: function() {
                                Job.userStartTime = Date.now();
                                administrativeSelectionLayer.features.forEach(
                                    function (feature) {
                                        Job.country.push( feature.attributes['region'] +
                                                ', ' + feature.attributes['country'])
                                    }
                                );
                                administrativeLayer.setVisibility(false);
                                administrativeSelectionLayer.setVisibility(false);
                                adminFeatureControl.deactivate();
				if (progressTracker.isDefault("definestudyarea")) {
				    progressTracker.alert( "definestudyarea", 
					"Don't forget to submit your selection.");
								}
                            }
                        }
                    }, {
                        xtype: 'definestudyyears',
                        id: 'definestudyyears',
                        title: '2. Define Outcome Period',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'limitplottypes',
                        id: 'limitplottypes',
                        title: '3. Limit Point Types',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'selectpolicyareas',
                        id: 'selectpolicyareas',
                        title: '4. Select Treatment Points',
                        layout: 'fit',
                        collapsible : true,
                        collapsed : true
                    }, {
                        xtype: 'selectcontrolareas',
                        id: 'selectcontrolareas',
                        title: '5. Select Control Points',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'matchsimilarplots',
                        id: 'matchsimilarplots',
                        title: '6. Select Matched Control Points',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'checkbalancestatistics',
                        id: 'checkbalancestatistics',
                        title: '7. Check Balance Statistics',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'measuretreatmenteffects',
                        id: 'measuretreatmenteffects',
                        title: '8. View Results',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'checksensitivity',
                        id: 'checksensitivity',
                        title: '9. Check Sensitivity',
                        collapsible: true,
                        collapsed: true
                    }, {
                        xtype: 'report',
                        id: 'report',
                        title: '10. Download Report',
                        collapsible: true,
                        collapsed: true
                    }]
                },
                {
                    xtype: 'container',
                    id: 'mapcontainer',
                    flex: 1,
                    html: "container",
                    layout: {
                        type: 'fit',
                        align: 'stretch'
                    },
                    items: [{
                        xtype: 'mainmap',
                        html: "<div id='map-panel'></div>"
                    }]
                }
            ]
        };

        Ext.Ajax.request({
            url: '/map/sess/',
            method: 'GET'
        });

        administrativeSelectionLayer.removeAllFeatures();
        Ext.Ajax.request({
            url: '/map/settings/reset',
            method: 'GET',
            success: function () {
                mexico.redraw(true);
            },
            failure: function () {
                mexico.redraw(true);
            }
        });

        administrativeLayer.setVisibility(false);
        administrativeSelectionLayer.setVisibility(false);
        adminFeatureControl.deactivate();
        this.callParent();
    }
});
