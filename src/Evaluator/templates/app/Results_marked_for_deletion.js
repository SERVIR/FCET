/**
 * @author vagrant
 */

Ext.define('Evaluator.view.Results', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.results',

    initComponent: function () {
        this.dockedItems = [{
            xtype: 'multislider',
            fieldLabel: 'Select Outcome Period',
            labelAlign: 'top',
            width: 175,
            margin: '5 5 5 5',
            values: [2005, 2011],
            increment: 1,
            minValue: 2001,
            maxValue: 2012
        }];
        //Listen for panel click and create results window
        //add table of ATT to results window
        //Matched Control Plots Fieldset
        //add visualize button
        //add download button
        //Matching Results FieldSet
        //add combobox
        //add visualize button
        //add download button
        //Propensity Score Regression FieldSet
        //add visualize button
        //add download button
        this.callParent();
    }
});
