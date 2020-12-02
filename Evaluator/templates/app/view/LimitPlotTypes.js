function submitFilterSettings(lowerBound, upperBound) {
    var myMask = new Ext.LoadMask(Ext.getBody(), {msg: "Please wait..."});
    myMask.show();

    return Ext.Ajax.request({
        url: '/map/forestfilter/set/' + lowerBound + '/'  + upperBound + '/',
        method: 'GET',
        success: function (response) {
            console.log(mexico.redraw(true));
            myMask.hide();
            return true
        },
        failure: function () {
            console.log('Failed to send geojson to server');
            mexico.redraw(true);
            myMask.hide();
            return false
        }
    });
}


Ext.define('Evaluator.view.LimitPlotTypes', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.limitplottypes',
    tools: [
		{
			type: 'progress',
			handler: function() {
				if (progressTracker.isAlert("limitpointtypes")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["limitpointtypes"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.limitPointTypes)}
		}
	],
    collapseFirst: false,
	modelUpdate: function() {
		if (progressTracker.isComplete('limitpointtypes')) {
			this.showCompleted();
		} else if (progressTracker.isAlert('limitpointtypes')) {
			this.showAlert();
		} else if (progressTracker.isDefault('limitpointtypes')) {
			this.showDefault();
		}
	},
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
    listeners: {
		collapse: function() {
			if (progressTracker.isDefault('limitpointtypes')) {
				progressTracker.alert("limitpointtypes", "Don't forget to submit your selection.");
			} 
		}
    },
    initComponent: function () {
		progressTracker.register(this);

        this.dockedItems = [{
            xtype: 'fieldset',
            title: 'Forest Cover Percentage',
            margin: '5 5 10 5',
            layout: {
                type: 'hbox'
            },
            items: [{
                xtype: 'label',
                id :'forest-slider-min-label',
                text: Job.minForestCover
            },{
                xtype: 'multislider',
                id: 'forest-slider',
                width: 175,
                margin: '5 5 5 5',
                values: [Job.minForestCover, Job.maxForestCover],
                increment: 1,
                minValue: Job.minForestCover,
                maxValue: Job.maxForestCover,
                listeners: {
                    changecomplete: function () {
                        this.up().down('#forest-slider-min-label').setText(this.getValues()[0]);
                        this.up().down('#forest-slider-max-label').setText(this.getValues()[1]);
                    }
                }
            },{
                xtype: 'label',
                id :'forest-slider-max-label',
                text: Job.maxForestCover
            }]
            },
//	{
//            xtype: 'fieldset',
//            title: 'Land Use Types',
//            layout: 'anchor',
//            frame: 'true',
//            margin: '5 5 10 5',
//            items: [{
//                xtype: 'checkbox',
//                boxLabel: 'AgroForest'
//            }, {
//                xtype: 'checkbox',
//                boxLabel: 'Agriculture'
//            }, {
//                xtype: 'checkbox',
//                boxLabel: 'Forest'
//            }]
//        },
	 {
            xtype: 'button',
            text: 'Submit Selection',
            cls: 'btn-success',
            handler: function () {
                var sliderValues = this.up().down("multislider").getValues();
                Job.minForestCover = sliderValues[0];
                Job.maxForestCover = sliderValues[1];
                var submitSuccess = submitFilterSettings(Job.minForestCover, Job.maxForestCover);
				if (submitSuccess) {
					progressTracker.completeLimitPointTypes();
				}
            }
        }];
        this.callParent();
    }

});
