/**
 * Ext.Loader
 */
Ext.Loader.setConfig({
    enabled: true,
    disableCaching: false,
    paths: {
        GeoExt: "../static/src/GeoExt",
        // for dev use
        Ext: "../static/js/ext/src"
    }
});

Ext.Loader.setPath('Ext.ux', '../static/src/js/ext/examples/ux')
Ext.require([
    // We need to require this class, even though it is used by Ext.EventObjectImpl
    // see: http://www.sencha.com/forum/showthread.php?262124-Missed-(-)-dependency-reference-to-a-Ext.util.Point-in-Ext.EventObjectImpl
    'Ext.util.Point'
]);

Ext.application({
    name: 'Evaluator',
    appFolder: 'app',
   // models: ['MTEresults', 'Song'],    
  //  stores: ['Stations', 'RecentSongs', 'SearchResults'],
    //controllers: ['Station', 'Song'],
    autoCreateViewport: true
});

var Job = {
    country: [],
    regionType: "",
    state: "",
    minForestCover: 1,
    maxForestCover: 100,
    agroforest: true,
    agriculture:true,
    forest: true,
    treatmentAreaOption: null,
    controlAreaOption: null,
    lowOutcomeYear: 2001,
    highOutcomeYear: 2012,
    matchingMethod: "Propensity Score Matching",
    matchingEstimator: "Nearest Neighbor 1-1",
    covariates: [],
    caliper: 0,
    common_support: true,
    standard_errors: null,
    outcome: "frst_ls",
    userStartTime: 0,
    userEndTime: 0
};

var panelDescriptions = {
	overview: 'The FCET measures the effect on deforestation of spatially delimited forest conservation policies (e.g. protected areas and payments for environmental services areas) controlling for the characteristics of the land where these policies are located. To use the tool, you must open, each of the 10 tools in this tool box in order starting from 1 and finishing at 10. Buttons colored green submit your modeling choices to FCET; you must click on them in order to proceed to the next step. For each tool, you can launch an information pop-up box like this one that provides brief guidance. For more detailed guidance and help, please consult the Instructions, which can be downloaded from the \u201CHow To\u201D menu in the dashboard.',
	defineStudyArea: 'This tool allows you to define a \u2018study area\u2019\u2014an area comprised of first-level administrative units (e.g., states in Mexico, departments in Guatemala) where you wish to evaluate the effect of the forest conservation policy. When you open this tool, the map will display administrative units with a blue outline. To include an administrative unit in your study area, single-click on it. The unit will then be displayed in beige and the forested points inside it will be displayed in green. For computational efficiency, only a random sample of the underlying sample points will displayed when the map is zoomed out. The full sample will only be displayed when you zoom in. To exclude an administrative unit that has been selected, single click on it. When you are finished defining the study area, click \u201CSubmit Selection.\u201D Administrative unit boundaries will disappear but green points inside the selected units will continue to be displayed.',
	defineStudyYears: 'This tool allows you to select \u2018outcome years\u2019\u2014the range of years between 2000-2012 over which the effect of the conservation policy on deforestation will be measured. For example, if you want to measure the effect of a policy on deforestation from 2004-2008, set the sliders to 2004 and 2008.',
	defineOutcomePeriod: 'This tool allows you to select \u2018outcome years\u2019\u2014the range of years between 2000-2012 over which the effect of the conservation policy on deforestation will be measured. For example, if you want to measure the effect of a policy on deforestation from 2004-2008, set the sliders to 2004 and 2008.',
	limitPointTypes: 'This tool allows you to exclude from the sample of points, those which have less than a minimum percentage forest cover and\/or those that have more than a maximum amount. For example, if you want to exclude points with less than 40% forest cover and more than 90% forest cover, move the sliders to 40 and 90.',
	selectTreatmentPoints: 'This tool allows you to select \u2018treatment points\u2019\u2014those points in the study area that have been subjected the forest conservation policy. You can do this in three ways: (i) uploading a shapefile that defines the spatial extent of the forest conservation policy, (ii) using the manual section tool, and (iii) using on-board data on the location of protected areas (PAs).',
	selectControlPoints: 'This tool allows you to select \u2018control points\u2019\u2014points in the study area that have not been subjected to the forest conservation policy and that are likely to include at least some points similar to those that have been subjected to it. Control points are those from among which matched control points will be selected in Step 6. You may want to limit control points to the points you believe have unobserved characteristics that affect deforestation, that is characteristics not captured by the observable characteristics (covariates) included in Step 6. You can select control points in  four ways: (i) selecting the entire study area, (ii) uploading a shapefile, (iii) using the manual section subtool, and (iv) using the proximity to policy areas subtool.',
	selectMatchedControlPoints: 'This tool allows you to select \u2018matched control points\u2019\u2014control points that are similar to treatment points. The FCET estimates the effect of forest conservation policies on deforestation by comparing the average deforestation rates on treatment points and matched control points.  To select matched control points, you must complete two steps: (i) select covariates: choose from a pre-determined list of 13 land characteristics (covariates), those that will be used to define \u2018similarity;\u2019 and (ii) click on the \u2018Run Statistical Matching\u2019 button which will cause FCET to display matched control points in yellow.',
	checkBalanceStatistics: 'This tool allows you to generate \u2018balance statistics\u2019\u2014statistics (in tabular and graphical format) that indicate how similar the matched control points are to the treatment points. The tool includes three subtools: (i) Plot Balance Statistics, which generates a graphical representation of similarity with respect to each covariate selected in Step 7; (ii) Tabulate Balance Statistics by Covariate, which generates the same information, but in tabular form; and (iii) View Summary Balance Statistics, which generates statistics that represent similarity across all covariates selected in Step 6. Median standardized bias below 3-5 percent is typically viewed as acceptable.',
	results: 'This tool allows you to view the results of the analysis of the forest conservation policy\u2019s effect on deforestation in tabular and graphical format.',
	checkSensitivity: 'This tool gives you a sense of how robust and reliable are the results from Step 8. More specifically, it checks the sensitivity to unobserved heterogeneity of the FCET\u2019s estimate of the effect of the forest conservation policy on deforestation. Further detail on this sensitivity analysis is provided \u201CFCET Metadata.pdf,\u201D which can be downloaded from the FCET dashboard.',
	report: 'This tool outputs a report in pdf format that contains all of the choices the user has made in completing Steps 2-7 above, and all of the balance statistics, results and sensitivity analyses generated in Steps 8 \u2013 10.'
};

var progressTracker = {
	completionData: {
		"definestudyarea": "incomplete",
		"defineoutcomeperiod": "incomplete",
		"limitpointtypes": "incomplete",
		"selecttreatmentpoints": "incomplete",
		"selectcontrolpoints": "incomplete",
		"selectmatchedcontrolpoints": "incomplete",
		"checkbalancestatistics": "incomplete",
		"results": "incomplete",
		"checksensitivity": "incomplete",
		"report": "incomplete"
	},
	completionAlerts: {
		"definestudyarea": "",
		"defineoutcomeperiod": "",
		"limitpointtypes": "",
		"selecttreatmentpoints": "",
		"selectcontrolpoints": "",
		"selectmatchedcontrolpoints": "",
		"checkbalancestatistics": "",
		"results": "",
		"checksensitivity": "",
		"report": ""
	},
	registeredViews: [],
	completeDefineStudyArea: function() {
		if (administrativeSelectionLayer.features.length > 0){
			this.completionData["definestudyarea"] = "complete";
		} else {
			this.completionData["definestudyarea"] = "alert";
			this.completionAlerts["definestudyarea"] = "You must select at least one region.";
		}

		var countryList = [];
		administrativeSelectionLayer.features.forEach(function(feature) {
			countryList.push(feature.attributes["country"]);
		});
		var allSame = function(array) {
			for(i=1; i<array.length; i++) {
				if(array[i] != array[0]) {
					return false;
				}
			}
			return true;
		}

		if (countryList.indexOf("Mexico") != -1 && !allSame(countryList)) {
			this.completionData["definestudyarea"] = "alert";
			this.completionAlerts["definestudyarea"] = "Due to data limitations, we cannot use data from Mexico concurrently with other countries.";
		}
		this.notify();
	},
	completeDefineOutcomePeriod: function() {
		this.completionData["defineoutcomeperiod"] = "complete";
		this.notify();
	},
	completeLimitPointTypes: function() {
		this.completionData["limitpointtypes"] = "complete";
		this.notify();
	},
	completeSelectTreatmentPoints: function() {
		this.completionData["selecttreatmentpoints"] = "complete";
		this.notify();
	},
	completeSelectControlPoints: function() {
		this.completionData["selectcontrolpoints"] = "complete";
		this.notify();
	},
	completeSelectMatchedControlPoints: function() {
		this.completionData["selectmatchedcontrolpoints"] = "complete";
		if (testStatistics.checkMedianBias) {
			this.completionData["checkbalancestatistics"] = "alert";
			this.completionAlerts["checkbalancestatistics"] = "Median bias exceeds 5, which indicates that the average treatment point and average control point are not particularly similar in terms of the covariates you have chosen in Step 6. Common causes of this problem include: (i) choosing a large number of covariates in Step 6, (ii) choosing treatment and control points in Steps 4 and 5 that do not contain points that are similar in terms of the covariates chosen in Step 6; (iii) choosing covariates in Step 6 that are not good predictors of which points are treated.";
		} else {
			this.completionData["checkbalancestatistics"] = "incomplete";
			this.completionAlerts["checkbalancestatistics"] = "";
		}
		this.notify();
	},
	completeCheckBalanceStatistics: function() {
		this.completionData["checkbalancestatistics"] = "complete";
		this.notify();
	},
	completeResults: function() {
		this.completionData["results"] = "complete";
		this.notify();
	},
	completeCheckSensitivity: function() {
		this.completionData["checksensitivity"] = "complete";
		this.notify();
	},
	completeReport: function() {
		this.completionData["report"] = "complete";
		this.notify();
	},
	alert: function(task, message) {
		this.completionData[task] = "alert";
		this.completionAlerts[task] = message;
		this.notify();
		return true
	},
	complete: function(task) {
		this.completionData[task] = "complete";
		this.notify();
		return true
	},
	incomplete: function(task) {
		this.completionData[task] = "incomplete";
		this.notify();
		return true
	},
	setAllIncomplete: function() {
		this.incomplete('definestudyarea');
		this.incomplete('defineoutcomeperiod');
		this.incomplete('limitpointtypes');
		this.incomplete('selecttreatmentpoints');
		this.incomplete('selectcontrolpoints');
		this.incomplete('selectmatchedcontrolpoints');
		this.incomplete('checkbalancestatistics');
		this.incomplete('results');
		this.incomplete('checksensitivity');
		this.incomplete('report');
	},
	isComplete: function(task) {
		if (this.completionData[task] == undefined) {
			throw Error("There is no " + task + " in completionData")
		}
		return this.completionData[task] == 'complete';
	},
	isAlert: function(task) {
		if (this.completionData[task] == undefined) {
			throw Error("There is no " + task + " in completionData")
		}
		return this.completionData[task] == 'alert';
	},
	isDefault: function(task) {
		if (this.completionData[task] == undefined) {
			throw Error("There is no " + task + " in completionData")
		}
		return this.completionData[task] == 'incomplete';
	},
	register: function(viewHandle) {
		this.registeredViews.push(viewHandle);
	},
	notify: function() {
		this.registeredViews.forEach(function(view) {view.modelUpdate()});
	}
}

/**
 * For dev purpose only
 */
var ctrl, map, mapPanel;
var testStore;
