/**
 * @author vagrant
 */

Ext.define('Evaluator.model.CheckSensitivity', {
    extend: 'Ext.data.Model',
    fields: ['gamma', 'q_plus', 'q_minus', 'p_plus', 'p_minus'],
    proxy: {
        type: 'ajax',
        url: '/tables/checksensitivity/',
        reader: {
            type: 'json'
        }
    }
});

var checkSensitivity = Ext.create('Ext.data.Store', {
    storeId: 'checkSensitivity',
    model: 'Evaluator.model.CheckSensitivity',
    autoLoad: false
});

var checkSensitivityPanel = {
    xtype: 'gridpanel',
    title: 'Rosenbaum Bounds',
    height: 260,
    width: 400,
    autoScroll: true,
    store: Ext.data.StoreManager.lookup('checkSensitivity'),
    columns: [
        {text: 'Gamma', dataIndex: 'gamma', flex: 1},
        {text: 'Q+', dataIndex: 'q_plus', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'Q-', dataIndex: 'q_minus', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'P-Value+', dataIndex: 'p_plus', renderer: Ext.util.Format.numberRenderer('0.00')},
        {text: 'P-Value-', dataIndex: 'p_minus', flex: 1, renderer: Ext.util.Format.numberRenderer('0.00')}]
};

Ext.define('Evaluator.view.CS', {
    extend: 'Ext.window.Window',
    alias: 'widget.cs',
    title: 'Check Sensitivity',
    height: 300,
    width: 400,
    initComponent: function () {
        checkSensitivity.load();
        this.dockedItems = [checkSensitivityPanel];
        this.callParent();
    }
});
