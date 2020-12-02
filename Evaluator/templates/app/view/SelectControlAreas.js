var toggleControl = function(element) {
    for (var key in drawControls) {
        var control = drawControls[key];
        if (element.value == key && element.checked) {
            control.activate();
        } else {
            control.deactivate();
        }
    }
}

var allowPan = function(element) {
    var stop = !element.checked;
    for (var key in drawControls) {
        drawControls[key].handler.stopDown = stop;
        drawControls[key].handler.stopUp = stop;
    }
}

var drawPolygon = function(element) {
    for (var key in drawControls) {
        var control = drawControls[key];
        if ("polygon" == key && element.pressed) {
            control.activate();
        } else {
            control.deactivate();
        }
    }
}

var removePolygon = function() {
    var control = map.getControl("OpenLayers_Control_DrawFeature_38");
    control.layer.removeAllFeatures();
    control.layer.redraw();
}

var sanitize_polygons = function(features) {
    function destroyIfEmpty(feature) {
        return !(feature.geometry.getArea() === 0);
    }

    return features.filter(destroyIfEmpty);
}

var sendCPolygons = function(geoJson) {
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();
    Ext.Ajax.request({
        url: '/map/selectcontrol',
        method: 'POST',
        jsonData: geoJson,
        success: function (response) {
            mexico.redraw(true);
            myMask.hide()
        },
        failure: function () {
            mexico.redraw(true);
            myMask.hide();
            console.log('Failed to send geojson to server');
        }
    });
};

var sendControlPolygons = function() {
    var geojson = new OpenLayers.Format.GeoJSON;
    var control = map.getControl("OpenLayers_Control_DrawFeature_38");
    var features = control.layer.getFeaturesByAttribute();
    var features = sanitize_polygons(features);
    var polygonsjson = geojson.write(features);
    Job.controlAreaOption = "Manual Selection";
    sendCPolygons(polygonsjson);
}

var clearControlPolygons = function() {
    Ext.Ajax.request({
        url: '../../map/clear/control',
        method: 'GET',
        success: function (response) {
            mexico.redraw(true);
        },
        failure: function () {
            mexico.redraw(true);
        }
    });
}

var sendControlByRadius = function(lowerBound, upperBound) {
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();

    Ext.Ajax.request({
        url: '/map/selectcontrolbyradius/' + lowerBound + '/' + upperBound + '/',
        method: 'GET',
        success: function (response) {
            mexico.redraw(true);
            myMask.hide();
        },
        failure: function () {
            mexico.redraw(true);
            myMask.hide();
        }
    });
};

var excludeControlByRadius = function(radius) {
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();

    Ext.Ajax.request({
        url: '/map/excludespillovers/' + radius + '/',
        method: 'GET',
        success: function (response) {
            mexico.redraw(true);
            myMask.hide();
        },
        failure: function () {
            console.log('Failed to send geojson to server');
            mexico.redraw(true);
            myMask.hide();
        }
    });
};




Ext.define('Evaluator.ClearControlButton', {
	extend: 'Ext.button.Button',
	alias: 'widget.clearcontrolbutton',
	layout: 'fit',
	anchor: '100%',
	text: 'Clear Control Point Selection',
	handler: clearControlPolygons,
	initComponent: function () {
		this.callParent();
	}
});

Ext.define('Evaluator.ExcludeSpillover', {
	extend: 'Ext.container.Container',
	alias: 'widget.excludespillover',
	layout: 'hbox',
	initComponent: function () {
		this.items = [{
				xtype: 'button',
				cls: 'btn-success',
				text: 'Exclude Spillover Areas Within',
				handler: function () {
				var radius = this.nextSibling('textfield').getValue();
				excludeControlByRadius(radius);
						}
				}, {
					xtype: 'textfield',
					margin: '0 10 0 10',
					width: 25,
					name: 'radius',
					value: 10
				}, {
					xtype: 'displayfield',
					value: 'KM'
				}];
		this.callParent();
	}
});
Ext.define('Evaluator.view.UploadControlWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.uploadcontrolwindow',
    items: {
        xtype: 'form',
        items: [
            {
                xtype: 'filefield',
                name: 'shapefile',
                allowBlank: false,
                buttonText: 'Upload shp',
                anchor: '50%',
                buttonOnly: false
            }, {
                xtype: 'filefield',
                name: 'indexfile',
                allowBlank: false,
                buttonText: 'Upload shx',
                anchor: '50%',
                buttonOnly: false
            }, {
                xtype: 'filefield',
                name: 'datafile',
                allowBlank: false,
                buttonText: 'Upload dbf',
                anchor: '50%',
                buttonOnly: false
            }, {
                xtype: 'filefield',
                name: 'prjfile',
                allowBlank: true,
                buttonText: 'Upload prj',
                anchor: '50%',
                buttonOnly: false
            },{
                xtype: 'button',
                text: 'Submit Selection',
                cls: 'btn-success',
                handler: function(fileUploadButton) {
                    var form = fileUploadButton.up('form').getForm();
                    if(form.isValid()) {
                        form.submit({
                            url: '../../map/service/geojson',
                            headers: {'Content-Type':'multipart/form-data; charset=UTF-8'},
                            method: 'POST',
                            waitMsg : 'Please wait...while uploading..!!',
                            success : function (form, action) {
                                sendCPolygons(action.result.geojson);
                                //Ext.Msg.alert('Upload file..', action.result.message);
                                Job.controlAreaOption = "Upload a Shapefile";
                                fileUploadButton.up('window').destroy();
								progressTracker.completeSelectControlPoints();
                            },
                            failure: function(form, action) {
                                Ext.Msg.alert('Upload file..', action.result.message);
                            }
                        });
            }}},{
                xtype: 'button',
                text: 'Cancel',
                handler: function(cancelButton) {
                    cancelButton.up('window').destroy();
                }
            }]
    }
});

Ext.define('Evaluator.view.SelectControlAreas', {
        extend: 'Ext.panel.Panel',
        alias: 'widget.selectcontrolareas',
        tools: [
		{
			type: 'progress',
			handler: function() {
				if (progressTracker.isAlert("selectcontrolpoints")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["selectcontrolpoints"])
				}
			}
		},
		{
            type: 'help',
            handler: function() {Ext.MessageBox.alert('', panelDescriptions.selectControlPoints)}
        }
		],
        collapseFirst: false,
		modelUpdate: function() {
			if (progressTracker.isComplete('selectcontrolpoints')) {
				this.showCompleted();
			} else if (progressTracker.isAlert('selectcontrolpoints')) {
				this.showAlert();
			} else if (progressTracker.isDefault('selectcontrolpoints')) {
				this.showDefault();
			}
		},
		showCompleted: function() {this.down('tool').setUI('check')},
		showAlert: function() {this.down('tool').setUI('alert')},
		showDefault: function() {this.down('tool').setUI('default')},
        listeners: {
            expand:	function() {
                this.up().down('definestudyarea').collapse();
                this.up().down('selectpolicyareas').collapse();
            },
            beforecollapse: function () {
                var drawButton = Ext.ComponentQuery.query("button[id='control-polygon-draw-button']")[0];
                drawButton.toggle(false);
                drawControls["polygon"].deactivate();
                removePolygon();
            },
			collapse: function() {
				if (progressTracker.isDefault('selectcontrolpoints')) {
					progressTracker.alert('selectcontrolpoints', "Don't forget to submit your selection.");
				} 
			}
        },
        initComponent: function () {
			progressTracker.register(this);
            this.dockedItems = [{
                xtype: 'fieldset',
                title: 'Option 1: Entire Study Area',
                collapsible: true,
                collapsed: true,
                margin: '5 5 10 5',
                items: [{
                    xtype: 'button',
                    layout: 'fit',
                    anchor: '100%',
                    text: 'Select Entire Study Area',
                    cls: 'btn-success',
                    handler: function () {
                        var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
                        myMask.show();
                        Ext.Ajax.disableCaching = false;
                        Ext.Ajax.request({
                            url: 'map/selectcontrolbystudyarea',
                            success: function () {
                                mexico.redraw(true);
                                Job.controlAreaOption = "Entire Study Area";
                                myMask.hide();
				progressTracker.completeSelectControlPoints();
                            },
                            failure: function () {
                                myMask.hide();
                            }
                        });
                    }
                },{
                    xtype: 'clearcontrolbutton'
                }, {
                    xtype:'excludespillover',
                }
]
            }, {
                xtype: 'fieldset',
                title: 'Option 2: Upload a Shapefile',
                collapsible: true,
                collapsed: true,
                margin: '5 5 10 5',
                items: [{
                    xtype: 'button',
		    cls: 'btn-success',
                    layout: 'fit',
                    anchor: '100%',
                    text: 'Upload Control Polygons',
                    handler: function() {
                        if (!Ext.getCmp('UCwindow')) {
                            Ext.create('widget.uploadcontrolwindow', {
                                id: 'UCwindow',
                                autoShow: true
                            });
                        } else {
                            Ext.getCmp('UCwindow').close();
                        }
                    }
                }, {
                    xtype: 'clearcontrolbutton'
                }, {
                	xtype:'excludespillover'
                }]
            }, {
                xtype: 'fieldset',
                title: 'Option 3: Manual Selection',
                collapsible: true,
                collapsed: true,
                margin: '5 5 10 5',
                items: [{
                    xtype: 'button',
                	id: 'control-polygon-draw-button',
                    text: 'Toggle Polygon Draw Tool',
                    layout: 'fit',
                    anchor: '100%',
                    enableToggle: true,
                    handler: drawPolygon
                }, {
                    xtype: 'button',
                    text: 'Clear Polygons',
                    layout: 'fit',
                    anchor: '100%',
                    handler: removePolygon
                }, {
                    xtype: 'button',
                    text: 'Select Control Points by Polygon',
                    cls: 'btn-success',
                    layout: 'fit',
                    anchor: '100%',
                    handler: function() {
                        sendControlPolygons();
                        removePolygon();
						progressTracker.completeSelectControlPoints();
                    }
                }, {
                    xtype: 'clearcontrolbutton'
                }, {
                	xtype:'excludespillover'
                }]
            }
//	{
//                xtype: 'fieldset',
//                title: 'Option 4: Proximity to Policy Area',
//                collapsible: true,
//                collapsed: true,
//                margin: '5 5 10 5',
//                items: [{
//                    xtype: 'multislider',
//                    fieldLabel: 'Radius (km)',
//                    layout: 'fit',
//                    anchor: '100%',
//                    labelAlign: 'top',
//                    width: 175,
//                    margin: '5 5 5 5',
//                    values: [0, 10],
//                    increment: 1,
//                    minValue: 0,
//                    maxValue: 50
//                }, {
//                    xtype: 'button',
//                    text: 'Select Control Points Within Bounds',
//                    cls: 'btn-success',
//                    layout: 'fit',
//                    anchor: '100%',
//                    handler: function () {
//                        var sliderValues = this.up().down('multislider').getValues();
//                        var lowerBound = sliderValues[0];
//                        var upperBound = sliderValues[1];
//                        Job.controlAreaOption = "Proximity to Policy Area";
//                        sendControlByRadius(lowerBound, upperBound);
//						progressTracker.completeSelectControlPoints();
//                    }
//                },{
//                    xtype: 'clearcontrolbutton'
//                }, {
//                	xtype:'excludespillover'
//                } ]
//            }
];

            this.callParent();
        }
    }
);
