// Helper Functions
var selectFeature = function(feature) {
    var fid = feature.fid.split('.')[1];
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();
    Ext.Ajax.request({
        url: function(fid) {
            return '/map/mapregions/'+fid+'/';
        }(fid),
        method: 'GET',
        async: false,
        success: function () {
            mexico.redraw(true);
            myMask.hide();
        },
        failure: function () {
            myMask.hide()
        }
    });
};

var unselectFeature = function(feature) {
    var fid = feature.fid.split('.')[1];
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();
    Ext.Ajax.request({
        url: function(country, regionType, region) {
            return '/map/unmapregions/'+fid+'/';
        }(fid),
        method: 'GET',
        async: false,
        success: function () {
            mexico.redraw(true);
            myMask.hide();
        },
        failure: function () {
            myMask.hide()
        }
    });
};
//var me = this, items = [], ctrl;
map = new OpenLayers.Map("map", {
        maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
        units:'m',
        projection: "EPSG:900913",
        displayProjection: new OpenLayers.Projection("EPSG:4326")
    });
mexico = new OpenLayers.Layer.WMS(
    // http://localhost/geoserver/evaluator/wms",
    "evaluator:django",
    "../../geoserver/evaluator/wms", {
        "LAYERS" : 'evaluator:usermap_fastfeature',
        "format" : 'image/gif',
        isBaseLayer : false,
        "transparent" : true,
        strategies: [new OpenLayers.Strategy.BBOX()]
    },
    // use sld hash to provide style data through xml
    {
        buffer : 0,
        singleTile : true,
        displayOutsideMaxExtent : false,
        yx : {
                'EPSG:900913 ' : true
            }
	});

//Create layers needed for app
var polygonLayer = new OpenLayers.Layer.Vector("Polygon Layer");

earth = new OpenLayers.Layer.XYZ(
    "Natural Earth",
    [
        "https://api.mapbox.com/styles/v1/aegornekov/ciri73brf0006gfm7360h7sws/tiles/${z}/${x}/${y}?fresh=false&access_token=pk.eyJ1IjoiYWVnb3JuZWtvdiIsImEiOiJjaXJpM3lzYmowMjAxZzFucmRrMW5sN2tyIn0.MUjp9RX5y-XVvA4tPmvl7Q",
    ], {
        attribution: "Tiles &copy; <a href='http://mapbox.com/'>MapBox</a>",
        sphericalMercator: true,
        wrapDateLine: true,
    }
);
var gphy = new OpenLayers.Layer.Google("Google Physical", {
    type:google.maps.MapTypeId.TERRAIN,
    'sphericalMercator':true,
    minZoomLevel:3, 
    maxZoomLevel:10, 
    fractionalZoom: true});

administrativeLayer = new OpenLayers.Layer.WMS(
    "evaluator:django",
    "/geoserver/evaluator/wms", {
        "LAYERS" : 'evaluator:regions_region',
        "format" : 'image/gif',
        isBaseLayer : false,
        "transparent" : true,
        projection: 'EPSG:4326',
        strategies: [new OpenLayers.Strategy.BBOX()]
    },
    // use sld hash to provide style data through xml
    {
        buffer : 0,
        singleTile : true,
        displayOutsideMaxExtent : false,
        yx : {
            'EPSG:900913 ' : false
        }
    });


//Set map projection --needed to keep maps in sync
aliasproj = new OpenLayers.Projection("EPSG:4326");
gphy.projection = aliasproj;

administrativeSelectionLayer = new OpenLayers.Layer.Vector("Selection");

//Add layers
var mapLayers = [administrativeLayer, administrativeSelectionLayer, earth, mexico, polygonLayer]
map.addLayers(mapLayers);

//Add Controls
drawControls = {
    polygon: new OpenLayers.Control.DrawFeature(polygonLayer, OpenLayers.Handler.Polygon)
};

adminFeatureControl = new OpenLayers.Control.GetFeature({
    protocol: OpenLayers.Protocol.WFS.fromWMSLayer(administrativeLayer),
    box: false,
    hover: false,
    click: true,
    maxFeatures: 1,
    multiple: true,
    single: true,
    toggle: true,
    clickout: false,
    filterType: OpenLayers.Filter.Spatial.CONTAINS
});

adminFeatureControl.events.register("featureselected", this, function(e) {
    test_event = e;
    if (administrativeSelectionLayer.visibility) {
        administrativeSelectionLayer.addFeatures([e.feature]);
        selectFeature(e.feature);
    }
});
adminFeatureControl.events.register("featureunselected", this, function(e) {
    test_event = e;
    if (administrativeSelectionLayer.visibility) {
        administrativeSelectionLayer.removeFeatures([e.feature]);
        unselectFeature(e.feature);
    }
});

// Initialize controllers

// Add controls to our single map
map.addControl(adminFeatureControl);

// Activate controls
adminFeatureControl.activate();

for(var key in drawControls) {
    map.addControl(drawControls[key]);
}
//map.zoomTo(4);
//map.zoomToMaxExtent();
//Set a focal point when the map initializes --default is 0,0 which does not render
//map.setCenter(new OpenLayers.LonLat(-80,-20).transform('EPSG:4326', 'EPSG:3857'));

map.addControl(new OpenLayers.Control.PanPanel());
map.addControl(new OpenLayers.Control.ZoomPanel());
var scaleLine = new OpenLayers.Control.ScaleLine();
scaleLine.maxWidth = 300;
map.addControl(scaleLine);
map.addControl(new OpenLayers.Control.ZoomBox());

Ext.define('Evaluator.view.MainMap', {
			// Ext.panel.Panel-specific options:
			extend : 'GeoExt.panel.Map',
			alias : 'widget.mainmap',
			border : 'false',
			layout : 'fit',
            layers : mapLayers,
			map : map,
			// GeoExt.panel.Map-specific options :
			center : new OpenLayers.LonLat(-95,20).transform('EPSG:4326', 'EPSG:3857'),
			zoom : 5,

			initComponent : function() {
				this.callParent(arguments);
			}
		});
