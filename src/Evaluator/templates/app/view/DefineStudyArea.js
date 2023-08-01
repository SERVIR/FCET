/* Define the Define Study Area view*/
Ext.define('Evaluator.view.DefineStudyArea', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.definestudyarea',
	tools: [
		{
			type: "progress",
			id: "define-study-area-progress",
			handler: function() {
				if (progressTracker.isAlert("definestudyarea")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["definestudyarea"])
				}
			}
		}, {
			type: "help",
			handler: function() {Ext.MessageBox.alert("", panelDescriptions.defineStudyArea)}
		}
],
	collapseFirst: false,
	modelUpdate: function() {
		if (progressTracker.isComplete('definestudyarea')) {
			this.showCompleted();
		} else if (progressTracker.isAlert('definestudyarea')) {
			this.showAlert();
		} else if (progressTracker.isDefault('definestudyarea')) {
			this.showDefault();
		}
	},
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
    listeners: {
    	expand: function() {
			administrativeLayer.setVisibility(true);
			administrativeSelectionLayer.setVisibility(true);
			adminFeatureControl.activate();
		},
		collapse: function() {
			Job.userStartTime = Date.now();
			administrativeLayer.setVisibility(false);
			administrativeSelectionLayer.setVisibility(false);
			adminFeatureControl.deactivate();
		}
    },
    initComponent: function () {
	progressTracker.register(this);

        this.dockedItems = [
			{
				xtype: 'button',
				text: 'Submit Selection',
				cls: 'btn-success',
				handler: function() {
					var parentPanel = this.up()
					progressTracker.completeDefineStudyArea();
					parentPanel.collapse();
				}
			}
			/*
			{
            xtype: 'combo',
            fieldLabel: 'By Country:',
			id: 'countryCombo',
            store:  countryStore,
            margin: '5 5 0 5',
			displayField: 'name',
		    valueField: 'name',
            listeners: {
				//expand: function() {countryStore.load()},
                select: function (combo, records) {
					Job.country = combo.getValue();
                	var data = records[0].sub_regions().data.items;
    				var store = subRegionStore; 
    				var component = Ext.getCmp('regionTypeCombo');
    				var newValue = 'Select a region type';
                	updateStudyAreaSelectors(data, store, component, newValue);
                },
                afterrender: function () {
                    this.setValue('Select a Country');
                }
            }
        }, {
            xtype: 'combo',
            fieldLabel: 'By Region Type:',
            id: 'regionTypeCombo',
            store: subRegionStore,
			displayField: 'name',
		    valueField: 'name',
            listeners: {
                select: function (combo, records) {
					Job.regionType = combo.getValue();
                	var record = records[0];
					regionStore.setProxy({
						type: 'memory',
						reader: {type:'json'},
						data: record.regions().data.items
					});
					regionStore.load();
					Ext.getCmp('regionCombo').setValue('Select a region');
                },
                afterrender: function () {
                    this.setValue('Select a region type');
                }
			},
            margin: '5 5 0 5'
        }, {
            xtype: 'combo',
            fieldLabel: 'By State:',
            id: 'regionCombo',
            store: regionStore,
            displayField: 'name',
            valueField: 'name',
            margin: '5 5 5 5',
            listeners: {
                select: function (combo, records) {
					// Record State/Region used for the job process and time started
					Job.state = combo.getValue();
					Job.userStartTime = Date.now();

					// Clear current map
                    Ext.Ajax.request({
                        url: '/map/clear',
                        method: 'GET',
                        success: function () {
                            mexico.redraw(true);
                        }
                    });
					// Get updated map with selected region
					var record = records[0];
					var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
					var country = Job.country;
					var regionType = Job.regionType;
					var region = Job.state;

					myMask.show();
					Ext.Ajax.request({
						url: function(country, regionType, region) {
								return '/map/mapregions/'+country+'/'+regionType+'/'+region+'/';
							}(country, regionType, region),
						method: 'GET',
						success: function () {
							mexico.redraw(true);
							var bounds = record.data.bounds;
							var boundsToZoomTo = new OpenLayers.Bounds(bounds);
							map.zoomToExtent(boundsToZoomTo.transform("EPSG:4326", "EPSG:900913"), false);
							myMask.hide();
						},
						failure: function () {myMask.hide()}
					});
                },


                afterrender: function () {
                    Ext.Ajax.request({
                        url: '/map/clear',
                        method: 'GET',
                        success: function () {
                            mexico.redraw(true);
                        }
                    });
                    this.setValue('Select a region');
                }
            }
        }*/
        ];
        this.callParent();
    }
});
