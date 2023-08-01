/**
 * @author vagrant
 */

function createCheckSensitivityPanel() {
    if (!Ext.getCmp('CSwindow')) {
        Ext.create('widget.cs', {
            id: 'CSwindow',
            autoShow: true
        });
    } else {
        Ext.getCmp('CSwindow').close();
    }
}

Ext.define('Evaluator.view.CheckSensitivity', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.checksensitivity',
	tools: [
		{
			type: "progress",
			handler: function() {
				if (progressTracker.isAlert("checksensitivity")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["checksensitivity"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.checkSensitivity)}
		}
	],
    collapseFirst: false,
    modelUpdate: function() {
		if (progressTracker.isComplete("checksensitivity")) {
			this.showCompleted();
		} else if (progressTracker.isAlert("checksensitivity")) {
			this.showAlert();
		} else if (progressTracker.isDefault("checksensitivity")) {
			this.showDefault();
		}
	},
    showCompleted: function() {this.down('tool').setUI('check')},
    showAlert: function() {this.down('tool').setUI('alert')},
    showDefault: function() {this.down('tool').setUI('default')},
    listeners: {
    	expand: function() {
            progressTracker.completeCheckSensitivity()
            console.log('thrown')	 
		}
    },
    initComponent: function () {
        progressTracker.register(this);
        this.dockedItems = [{
                xtype: 'button',
                text: 'Compute Rosenbaum Bounds',
		handler: createCheckSensitivityPanel
            }];
        this.callParent();
    }
});
