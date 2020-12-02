/**
 * @author vagrant
 */
var report_url = function() {
    var width = map.getCurrentSize()['w'];
    var height = map.getCurrentSize()['h'];

    return '/map/report/' + map.calculateBounds().toString() + '/' + width + '/' + height + '/';
};

Ext.define('Evaluator.view.Report', {
    extend : 'Ext.panel.Panel',
    alias : 'widget.report',
	tools: [
		{
			type: "progress",
			handler: function() {
				if (progressTracker.isAlert("report")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["report"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.report)}
		}
	],
	modelUpdate: function() {
		if (progressTracker.isComplete("report")) {
			this.showCompleted();
		} else if (progressTracker.isAlert("report")) {
			this.showAlert();
		} else if (progressTracker.isDefault("report")) {
			this.showDefault();
		}
	},
	collapseFirst: false,
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
    listeners: {
    	expand: function() {
            progressTracker.completeReport()
		}
    },
    initComponent : function() {
        progressTracker.register(this);
		testPanel = this;
        this.dockedItems = [{
                xtype : 'button',
                text : 'Download Complete Report',
                handler: function() {
                    var windowObjectReference = window.open(report_url());
					this.up('panel').collapse()
                }
        }];
        this.callParent();
    }
});
