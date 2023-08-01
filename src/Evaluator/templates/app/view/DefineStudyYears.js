//hack, change this
Ext.define('Evaluator.view.DefineStudyYears', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.definestudyyears',
	tools: [
		{
			type: "progress",
			handler: function() {
				if (progressTracker.isAlert("defineoutcomeperiod")) {
					Ext.MessageBox.alert("", progressTracker.completionAlerts["defineoutcomeperiod"])
				}
			}
		},
		{
			type: 'help',
			handler: function() {Ext.MessageBox.alert('', panelDescriptions.defineStudyYears)}
		}
],
	collapseFirst: false,
	modelUpdate: function() {
		if (progressTracker.isComplete('defineoutcomeperiod')) {
			this.showCompleted();
		} else if (progressTracker.isAlert('defineoutcomeperiod')) {
			this.showAlert();
		} else if (progressTracker.isDefault('defineoutcomeperiod')) {
			this.showDefault();
		}
	},
	showCompleted: function() {this.down('tool').setUI('check')},
	showAlert: function() {this.down('tool').setUI('alert')},
	showDefault: function() {this.down('tool').setUI('default')},
	listeners: {
		collapse: function() {
			if (progressTracker.isDefault('defineoutcomeperiod')) {
				progressTracker.alert("defineoutcomeperiod", "Don't forget to submit your selection.");
			} 
		}
	},
	initComponent: function () {
		progressTracker.register(this);
		this.dockedItems = [{
			xtype: 'fieldset',
			title: 'Outcome Period',
			margin: '5 5 10 5',
			layout: {
				type: 'hbox'
			},
			items: [{
				xtype: 'label',
				id :'year-slider-low-label',
				text: Job.lowOutcomeYear
			},{
				xtype: 'multislider',
				id: 'year-slider',
				width: 175,
				margin: '5 5 5 5',
				values: [Job.lowOutcomeYear, Job.highOutcomeYear],
				increment: 1,
				minValue: Job.lowOutcomeYear,
				maxValue: Job.highOutcomeYear,
				flex: 1,
				listeners: {
					changecomplete: function () {
						//hack, change this to use a store
						Job.lowOutcomeYear = this.getValues()[0];
						this.up().down('#year-slider-low-label').setText(Job.lowOutcomeYear);
						Job.highOutcomeYear = this.getValues()[1];
						this.up().down('#year-slider-high-label').setText(Job.highOutcomeYear);
					}
				}
			},{
				xtype: 'label',
				id :'year-slider-high-label',
				text: Job.highOutcomeYear
			}]},
			{
				xtype: 'button',
				cls: 'btn-success',
				text: 'Submit Selection',
				handler: function () {
					progressTracker.completeDefineOutcomePeriod();
				}
			}];
			this.callParent();
		}
	});
