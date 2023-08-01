//hack, change this

Ext.define('Evaluator.view.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.overview',
    tools: [{
        type: 'help',
        handler: function() {Ext.MessageBox.alert('', panelDescriptions.overview)}
    }],
	collapseFirst: false,
    initComponent: function () {
        this.callParent();
    }
});
