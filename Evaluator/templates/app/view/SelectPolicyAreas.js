var toggleControl = function(element) {
    for (var key in drawControls) {
        var control = drawControls[key];
        if (element.value == key && element.checked) {
            control.activate();
        } else {
            control.deactivate();
        }
    }
};

var allowPan = function(element) {
    var stop = !element.checked;
    for (var key in drawControls) {
        drawControls[key].handler.stopDown = stop;
        drawControls[key].handler.stopUp = stop;
    }
};

var drawPolygon = function(element) {
    for (var key in drawControls) {
        var control = drawControls[key];
        if ("polygon" == key && element.pressed) {
            control.activate();
        } else {
            control.deactivate();
        }
    }
};

var removePolygon = function() {
    var control = map.getControl("OpenLayers_Control_DrawFeature_38");
    control.layer.removeAllFeatures();
    control.layer.redraw();
};

var sanitize_polygons = function(features) {
    function destroyIfEmpty(feature) {
        return !(feature.geometry.getArea() === 0);
    }
    return features.filter(destroyIfEmpty);
};

var sendTPolygons = function(geoJson) {
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();
    Ext.Ajax.request({
        url: '../../map/selecttreatment',
        method: 'POST',
        timeout: 90000,
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

var sendTreatmentPolygons = function() {
    var geojson = new OpenLayers.Format.GeoJSON;
    var control = map.getControl("OpenLayers_Control_DrawFeature_38");
    var features = control.layer.getFeaturesByAttribute();
    var features = sanitize_polygons(features);
    var polygonsjson = geojson.write(features);
    Job.treatmentAreaOption = "Manual Selection";
    sendTPolygons(polygonsjson);
};

var clearTreatmentPolygons = function() {
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();
    Ext.Ajax.request({
        url: '../../map/clear/treatment',
        method: 'GET',
        success: function (response) {
            mexico.redraw(true);
            myMask.hide()
        },
        failure: function () {
            console.log('Failed to request to server');
            mexico.redraw(true);
            myMask.hide();
        }
    });
};




Ext.define('policy_areas', {
   extend: 'Ext.data.Model',
    fields: [{name: 'name', type: 'string'}]
});

var policy_areas = Ext.create('Ext.data.Store', {
    model: 'policy_areas',
    proxy: {
        type: 'ajax',
        url : 'map/policy_areas/',
        reader: {
            type: 'json',
            root: 'root'
        }
    }
});

Ext.define('Evaluator.ClearTreatmentButton', {
    extend: 'Ext.button.Button',
    alias: 'widget.cleartreatmentbutton',
    layout: 'fit',
    anchor: '100%',
    text: 'Clear Treatment Point Selection',
    handler: clearTreatmentPolygons,
    initComponent: function() {
        this.callParent();
    }
});

Ext.define('Evaluator.view.UploadTreatmentWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.uploadtreatmentwindow',
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
            }, {
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
                            waitMsg : 'Please wait...while uploading',
                            success : function (form, action) {
                                sendTPolygons(action.result.geojson);
                                //Ext.Msg.alert('Upload file..', action.result.message);
                                Job.treatmentAreaOption = "Upload a Shapefile";
                                fileUploadButton.up('window').destroy();
								progressTracker.completeSelectTreatmentPoints();
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

Ext.define('Evaluator.view.SelectPolicyAreas', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.selectpolicyareas',
    tools: [
		{
			type: 'progress',
			handler: function() {
				if (progressTracker.isAlert("selecttreatmentpoints")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["selecttreatmentpoints"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.selectTreatmentPoints)}
		}
    ],
    collapseFirst: false,
    collapsible: true,
    collapsed: true,
	modelUpdate: function() {
		if (progressTracker.isComplete('selecttreatmentpoints')) {
			this.showCompleted();
		} else if (progressTracker.isAlert('selecttreatmentpoints')) {
			this.showAlert();
		} else if (progressTracker.isDefault('selecttreatmentpoints')) {
			this.showDefault();
		}
	},
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
    listeners: {
        expand:	function() {
            this.up().down('definestudyarea').collapse();
            this.up().down('selectcontrolareas').collapse();
        },
        beforecollapse: function () {
            var drawButton = Ext.ComponentQuery.query("button[id='treatment-polygon-draw-button']")[0];
            drawButton.toggle(false);
            drawControls["polygon"].deactivate();
            removePolygon();
        },
		collapse: function() {
			if (progressTracker.isDefault('selecttreatmentpoints')) {
				progressTracker.alert("selecttreatmentpoints", "Don't forget to submit your selection");
			} 
		}
    },
    initComponent: function() {
		progressTracker.register(this);
        this.dockedItems = [{
            xtype: 'fieldset',
            title: 'Option 1: Upload a Shapefile',
            collapsible: true,
            collapsed: true,
            margin: '5 5 10 5',
            items: [{
                xtype: 'button',
		cls: 'btn-success',
                text: 'Upload Treatment Polygons',
                anchor: '100%',
                handler: function() {
                    if (!Ext.getCmp('UTwindow')) {
                        Ext.create('widget.uploadtreatmentwindow', {
                            id: 'UTwindow',
                            autoShow: true
                        });
                    } else {
                        Ext.getCmp('UTwindow').close();
                    }
                }
            },{
                xtype: 'cleartreatmentbutton'
            }]
        }, {
            xtype: 'fieldset',
            title: 'Option 2: Manual Selection',
            collapsible: true,
            collapsed : true,
            margin: '5 5 10 5',
            items: [{
                xtype: 'button',
                id: 'treatment-polygon-draw-button',
                text: 'Toggle Polygon Selection Tool',
                anchor: '100%',
                enableToggle: true,
                handler: drawPolygon
            }, {
                xtype: 'button',
                text: 'Clear Polygons',
                anchor: '100%',
                handler: removePolygon
            }, {
                xtype: 'button',
                text: 'Submit Selection',
                cls: 'btn-success',
                anchor: '100%',
                handler: function() {
                    sendTreatmentPolygons();
                    removePolygon();
					progressTracker.completeSelectTreatmentPoints();
                }
            }, {
                xtype: 'cleartreatmentbutton'
            }]
        }, {
            xtype: 'fieldset',
            title: 'Option 3: Select PA Tool',
            collapsible: true,
            collapsed : true,
            margin: '5 5 10 5',
            items: [{
                xtype: 'combobox',
                store: policy_areas,
                fieldLabel: 'Select a Policy',
                valueField: 'name',
                displayField: 'name',
                anchor: '100%'

            },{
                xtype: 'button',
                text: 'Submit Selection',
                cls: 'btn-success',
                anchor: '100%',
                handler: function () {
                    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
                    myMask.show();
                    var policy_name = this.previousSibling().getValue();
                    if (policy_name !== null) {
                        Ext.Ajax.request({
                            url: 'map/policy_areas/',
                            method: 'POST',
                            jsonData: {
                                policy_name: policy_name
                            },
                            timeout: 120000,
                            success: function () {
                                mexico.redraw(true);
                                Job.treatmentAreaOption = "Select Policy";
                                myMask.hide();
								progressTracker.completeSelectTreatmentPoints();
                            },
                            failure: function () {
                                mexico.redraw(true);
                                myMask.hide();
                            }
                        });
                    } else {
                        myMask.hide();
                    }
                }
            },{
                xtype: 'cleartreatmentbutton',
            }]
        }];
        this.callParent();
    }
});
