Ext.define('Evaluator.store.SearchResults', {
    extend: 'Ext.data.Store',
    requires: 'Evaluator.model.Station',
    model: 'Evaluator.model.Station',

    autoLoad: true,
    
    // Overriding the model's default proxy
    proxy: {
        type: 'ajax',
        url: 'data/searchresults.json',
        reader: {
            type: 'json',
            root: 'results'
        }
    }
});