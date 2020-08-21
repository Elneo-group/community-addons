/*#############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################*/

openerp.tree_date_search_extension = function(instance) {
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
/*
    function synchronized(fn) {
        var fn_mutex = new $.Mutex();
        return function () {
            var obj = this;
            var args = _.toArray(arguments);
            return fn_mutex.exec(function () {
                if (obj.isDestroyed()) { return $.when(); }
                return fn.apply(obj, args)
            });
        };
    }*/
    // Replace the path
    instance.web.views.map['list'] = 'instance.tree_date_search_extension.ListView';

    instance.tree_date_search_extension.ListView = instance.web.ListView.extend({
        init: function(parent, dataset, view_id, options) {
            this._super.apply(this, arguments);

            if ("dates_filter" in dataset.context){
                this.dates_filter = dataset.context["dates_filter"]
                this.current_date_from  = [];
                this.current_date_to  = [];
            }
            this.search_extension_loaded = false;
        },
        do_load_state: function(state, warm) {
            if (this.dates_filter && this.dates_filter.length > 0){
                var $ui_toolbar_loc = $('.ui-toolbar:last').show();
            }
            else{
                $('.ui-toolbar:last').hide();
            }
            return this._super.apply(this, arguments);
        },
        load_list: function(data) {
            var self = this;
            var tmp = this._super.apply(this, arguments);
            if (!this.search_extension_loaded){
                this.date_field_string = [];
                for (i in this.dates_filter){
                    var date_field = this.dates_filter[i];
                    for (col in this.columns){
                        if (this.columns[col].name == date_field){
                            this.date_field_string[date_field] = this.columns[col].string;
                            break;
                        }
                    }
                }
                if (this.dates_filter && this.dates_filter.length > 0){
                    this.$el.parent().prepend(QWeb.render('SearchExtension', {widget: this}));
                    var $ui_toolbar_loc = $('.ui-toolbar:last').show();
                    //var $ui_toolbar_loc = $('.ui-toolbar:last').show().empty();
                    for (i in this.dates_filter){
                        var date_field = this.dates_filter[i];
                        // add xml data
                        var date_div = $("<div class='oe_form_dropdown_section' style='margin-right:8px; display: inline;'>" +
                            "<h4 style='display: inline;'>" + this.date_field_string[date_field] + " :</h4>"+
                            "<div class='oe_form' style='display: inline; margin-right:4px;' >"+
                            "    <span class='oe_gantt_filter_from_" + date_field + "'></span>"+
                            "</div>"+
                            "<div class='oe_form' style='display: inline;' >"+
                            "    <span class='oe_gantt_filter_to_" + date_field + "' ></span>"+
                            "</div></div>");

                        date_div.appendTo($ui_toolbar_loc);

                        this.value = new (instance.web.search.custom_filters.get_object('date'))
                            (this, {"selectable":true,
                                "name":"oe_gantt_filter_from_" + date_field, 
                                "type": "date",
                                "string":this.date_field_string[date_field]});
                        var $value_loc = $('.oe_gantt_filter_from_' + date_field + ':last').show().empty();
                        this.value.appendTo($value_loc);

                        this.value = new (instance.web.search.custom_filters.get_object('date'))
                            (this, {"selectable":true,
                                "name":"oe_gantt_filter_to_" + date_field, 
                                "type": "date",
                                "string":this.date_field_string[date_field]});
                        var $value_loc = $('.oe_gantt_filter_to_' + date_field + ':last').show().empty();
                        this.value.appendTo($value_loc);

                        var $oe_gantt_filter_from = $('.oe_gantt_filter_from_' + date_field);
                        var $oe_gantt_filter_to = $('.oe_gantt_filter_to_' + date_field);

                        $('.oe_gantt_filter_from_' + date_field + ':last .oe_datepicker_master').attr(
                            "placeholder", _t("From"));
                        $('.oe_gantt_filter_to_' + date_field + ':last .oe_datepicker_master').attr(
                            "placeholder", _t("To"));

                        // on_change
                        this.$el.parent().find(
                            '.oe_gantt_filter_from_' + date_field + ':last .oe_datepicker_master').change(function() {
                            var elem = this.parentElement.parentElement.parentElement.className;
                            var res = elem.split("oe_gantt_filter_from_");
                            self.current_date_from[res[1]] = this.value === '' ? null : this.value;
                            if (self.current_date_from[res[1]]){
                                self.current_date_from[res[1]] = instance.web.parse_value(
                                    self.current_date_from[res[1]], {
                                    "widget": "date"
                                });
                            }
                            self.do_search(self.last_domain, self.last_context, self.last_group_by);
                        });
                        this.$el.parent().find(
                            '.oe_gantt_filter_to_' + date_field + ':last .oe_datepicker_master').change(function() {
                            var elem = this.parentElement.parentElement.parentElement.className;
                            var res = elem.split("oe_gantt_filter_to_");
                            self.current_date_to[res[1]] = this.value === '' ? null : this.value;
                            if (self.current_date_to[res[1]]){
                                self.current_date_to[res[1]] = instance.web.parse_value(
                                    self.current_date_to[res[1]], {
                                    "widget": "date"
                                });
                            }
                            self.do_search(self.last_domain, self.last_context, self.last_group_by);
                        });
                        this.on('edit:after', this, function () {
                            self.$el.parent().find('.oe_gantt_filter_from_' + date_field + ':last').attr('disabled', 'disabled');
                            self.$el.parent().find('.oe_gantt_filter_to_' + date_field + ':last').attr('disabled', 'disabled');
                        });
                        this.on('save:after cancel:after', this, function () {
                            self.$el.parent().find('.oe_gantt_filter_from_' + date_field + ':last').removeAttr('disabled');
                            self.$el.parent().find('.oe_gantt_filter_to_' + date_field + ':last').removeAttr('disabled');
                        });
                    }
                }
                else{
                    $('.ui-toolbar:last').hide();
                }
                this.search_extension_loaded = true;
            }
            return tmp;
        },
        do_search: function(domain, context, group_by) {
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            return self.search_by_selection();
        },
        search_by_selection: function() {
            var self = this;
            var domain = [];

            for (from in self.current_date_from){
                if (self.current_date_from[from])
                    domain.push([from, '>=', self.current_date_from[from]]);
            }
            for (to in self.current_date_to){
                if (self.current_date_to[to])
                    domain.push([to, '<=', self.current_date_to[to]]);
            }

            return self.old_search(new instance.web.CompoundDomain(
                self.last_domain, domain), self.last_context, self.last_group_by);
        },
    });

};
