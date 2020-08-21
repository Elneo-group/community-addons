(function() {

var instance = openerp;

var _t = instance.web._t;

var normalize_format = function (format) {
    return Date.normalizeFormat(instance.web.strip_raw_chars(format));
};

instance.web.list.Column = instance.web.list.Column.extend({

    // format the datetime_custo as user timezone & format langue like a 
    // datetime when readonly mode
    _format: function (row_data, options) {
        var value = row_data[this.id].value;
        var descriptor = this;
        var value_if_empty = options.value_if_empty;
        
        var l10n = _t.database.parameters;
        var res = false;
        switch (this.widget || this.type || (this.field && this.field.type)) {
            case 'datetime_custo':
                if (typeof(value) == "string")
                    value = instance.web.auto_str_to_date(value);
                if (value != false){
                    res = value.toString(normalize_format(l10n.date_format)
                            + ' ' + normalize_format(l10n.time_format));
                }
        }
        if (res != false){
            return _.escape(res)
        }
        return this._super(row_data, options);

    }
});



})();
