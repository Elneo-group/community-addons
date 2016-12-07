openerp.datetime_widget = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.datetime_widget.DateTimeWidgetCusto = instance.web.Widget.extend({
        template: "datepicker_custo",
        jqueryui_object: 'datetimepicker',
        type_of_date: "datetime",
        events: {
            'change .oe_datepicker_master': 'change_datetime',
            'keypress .oe_datepicker_master': 'change_datetime',
        },
        init: function(parent) {
            this._super(parent);
            this.name = parent.name;
            this.minute_type = parent.minute_type;
            this.mindate = parent.mindate || false;
            this.maxdate = parent.maxdate || false;
        },
        start: function() {
            var self = this;
            this.$input = this.$el.find('input.oe_datepicker_master');
            this.$input_picker = this.$el.find('input.oe_datepicker_container');

            //this.$select_hour = $(".hour")[0];
            this.$select_hour = this.$el.find("select.hour");

            //this.$select_min = $(".min")[0];
            //this.$select_min_number = $(".min_number")[0];
            this.$select_min = this.$el.find("select.min");
            this.$select_min_number = this.$el.find("input.min_number");


            this.$el.find("select.hour").show();
            if (this.minute_type == 'quarter') {
                this.$el.find("select.min").show();
            } else {
                this.$el.find("input.min_number").show();
            }

            // add the options on the selection field
            var hour = ['00', '01', '02', '03', '04', '05', '06', '07', '08',
                '09', '10', '11', '12', '13', '14', '15', '16', '17', '18',
                '19', '20', '21', '22', '23',
            ];

            var _t = instance.web._t;
            var l10n = _t.database.parameters;
            // return value.toString(normalize_format(l10n.date_format)
            //             + ' ' + normalize_format(l10n.time_format));

            /*if (l10n.time_format.indexOf("%I") != -1 && l10n.time_format.indexOf("%p") != -1){
                hour = ['00', '01', '02', '03', '04', '05', '06', '07', '08',
                    '09', '10', '11'
                ];
                this.$el.find(".am_pm_select").show();
            }*/

            var min = ['00', '15', '30', '45'];
            for (i in hour) {
                this.$select_hour[0].options[
                    this.$select_hour[0].options.length] = new Option(
                    hour[i], hour[i]);
            }
            for (i in min) {
                this.$select_min[0].options[
                    this.$select_min[0].options.length] = new Option(
                    min[i], min[i]);
            }
            this.$select_hour[0].onchange = this.on_change_hour;
            this.$select_min[0].onchange = this.on_change_min;
            this.$select_min_number[0].onchange = this.on_change_min_number;

            $.datepicker.setDefaults({
                clearText: _t('Clear'),
                clearStatus: _t('Erase the current date'),
                closeText: _t('Done'),
                closeStatus: _t('Close without change'),
                prevText: _t('<Prev'),
                prevStatus: _t('Show the previous month'),
                nextText: _t('Next>'),
                nextStatus: _t('Show the next month'),
                currentText: _t('Today'),
                currentStatus: _t('Show the current month'),
                monthNames: Date.CultureInfo.monthNames,
                monthNamesShort: Date.CultureInfo.abbreviatedMonthNames,
                monthStatus: _t('Show a different month'),
                yearStatus: _t('Show a different year'),
                weekHeader: _t('Wk'),
                weekStatus: _t('Week of the year'),
                dayNames: Date.CultureInfo.dayNames,
                dayNamesShort: Date.CultureInfo.abbreviatedDayNames,
                dayNamesMin: Date.CultureInfo.shortestDayNames,
                dayStatus: _t('Set DD as first week day'),
                dateStatus: _t('Select D, M d'),
                firstDay: Date.CultureInfo.firstDayOfWeek,
                initStatus: _t('Select a date'),
                isRTL: false
            });
            $.timepicker.setDefaults({
                format:'Y-m-d',
                timeOnlyTitle: _t('Choose Time'),
                timeText: _t('Time'),
                hourText: _t('Hour'),
                minuteText: _t('Minute'),
                //secondText: _t('Second'),
                currentText: _t('Now'),
                closeText: _t('Done')
            });
            // customise the picker field by field
            this.picker({
                onClose: this.on_picker_close,
                onSelect: this.on_picker_select,
                changeMonth: true,
                changeYear: true,
                showWeek: true,
                showButtonPanel: true,
                firstDay: Date.CultureInfo.firstDayOfWeek,
                // add min and max date:
                minDate: this.mindate && this.mindate || null,
                maxDate: this.maxdate && this.maxdate || null,
            });

            // Some clicks in the datepicker dialog are not stopped by the
            // datepicker and "bubble through", unexpectedly triggering the bus's
            // click event. Prevent that.
            this.picker('widget').click(function(e) {
                e.stopPropagation();
            });

            this.$el.find('img.oe_datepicker_trigger').click(function() {
                if (self.get("effective_readonly") || self.picker('widget').is(':visible')) {
                    self.$input.focus();
                    return;
                }
                self.picker('setDate', self.get('value') ? instance.web.auto_str_to_date(self.get('value')) : new Date());
                self.$input_picker.show();
                self.picker('show');
                self.$input_picker.hide();
            });
            this.set_readonly(false);
            this.set({
                'value': false
            });
        },
        picker: function() {
            return $.fn[this.jqueryui_object].apply(this.$input_picker, arguments);
        },
        on_picker_select: function(text, instance_) {
            var date = this.picker('getDate');
            this.$input
                .val(date ? this.format_client(date) : '')
                .change()
                .focus();
        },
        on_picker_close: function(text, instance_) {
            var date = this.picker('getDate');
            this.$input
                .val(date ? this.format_client(date) : '')
                .change();

            // this doesn't work on firefox..
            var clickEvent = document.createEvent('MouseEvents');
            clickEvent.initEvent('mousedown', true, true);
            this.$select_hour[0].dispatchEvent (clickEvent);

            /*
            var event = new MouseEvent('mousedown', {
                'view': window,
                'bubbles': true,
                'cancelable': true
              });
            this.$select_hour[0].dispatchEvent (event);
            $('.oe_inlinehour').dispatchEvent(event);
            */
            this.$select_hour[0].focus();
        },
        on_change_hour: function(text, instance_) {
            this.change_datetime(text);
            //var event;
            //event = document.createEvent('MouseEvents');
            //event.initMouseEvent('mousedown', true, true, window);
            // change minute is not enought used so we don't want the select was automatically opened..
            // but we can change the focus on it.
            //this.$select_min[0].dispatchEvent(event);
            if (this.minute_type == 'quarter') {
                this.$select_min[0].focus();
            } else {
                this.$select_min_number[0].focus();
            }
        },
        on_change_min: function(text, instance_) {
            this.change_datetime(text);
        },
        on_change_min_number: function(text, instance_) {
            this.change_datetime(text);
        },
        get_minutes_value: function(min) {
            // type = "normal" or "quarter"
            if (this.minute_type == 'quarter') {
                var allowed_min = ['00', '15', '30', '45'];
                if (min in allowed_min)
                    return min

                // this should never be used
                if (min < 7.5)
                    return '00'
                if (min < 21.5)
                    return '15'
                if (min < 37.5)
                    return '30'
                else
                    return '45'
            }
            return min
        },
        set_value: function(value_) {
            var formated_client_datetime_value = this.format_client_datetime(value_);
            var date = formated_client_datetime_value.split(" ")[0];
            if (value_){
                var d = instance.web.auto_str_to_date(value_);
                var hour   = d.getHours();
                var minute = d.getMinutes();
                var second = d.getSeconds();
                if(hour.toString().length == 1){
                    hour = '0' + hour.toString();
                }
                /*var ap = "AM";
                if (hour   > 11) { ap = "PM";             }
                if (hour   > 12) { hour = hour - 12;      }
                if (hour   == 0) { hour = 12;             }
                if (hour   < 10) { hour   = "0" + hour;   }
                if (minute < 10) { minute = "0" + minute; }
                if (second < 10) { second = "0" + second; }*/

                this.$select_hour.val(hour);
                //this.$el.find(".am_pm_select").val(ap);
                var m = this.get_minutes_value(minute);
                if (this.minute_type == 'quarter') {
                    this.$select_min.val(m);
                } else {
                    this.$select_min_number.val(m);
                }
            }

            this.$input.val(value_ ? date : '');
            this.set({
                'value': value_
            });
        },
        get_value: function() {
            var value = this.get('value');
            return value
        },
        set_value_from_ui_: function() {
            var value_ = this.$input.val() || false;
            if (value_ != false) {
                var hour_ = this.$select_hour[0].options[this.$select_hour[0].selectedIndex].text;
                var min_;
                if (this.minute_type == 'quarter') {
                    min_ = this.$select_min[0].options[this.$select_min[0].selectedIndex].text;
                } else {
                    min_ = this.$select_min_number[0].value;
                }
                value_ = value_ + ' ' + hour_ + ':' + min_ + ':00'
            }
            var v = this.parse_client(value_);
            this.set({
                'value': v
            });
        },
        set_readonly: function(readonly) {
            this.readonly = readonly;
            this.$input.prop('readonly', this.readonly);
            this.$el.find('img.oe_datepicker_trigger').toggleClass('oe_input_icon_disabled', readonly);
        },
        is_valid_: function() {
            var value_ = this.$input.val();
            if (value_ === "") {
                return true;
            } else {
                try {
                    this.parse_client(value_);
                    return true;
                } catch (e) {
                    return false;
                }
            }
        },
        parse_client: function(v) {
            return instance.web.parse_value(v, {
                "widget": "datetime"
            });
        },
        format_client_datetime: function(v) {
            return instance.web.format_value(v, {
                "widget": "datetime"
            });
        },
        format_client: function(v) {
            return instance.web.format_value(v, {
                "widget": this.type_of_date
            });
        },
        change_datetime: function(e) {
            if ((e.type !== "keypress" || e.which === 13) && this.is_valid_()) {
                this.set_value_from_ui_();
                this.trigger("datetime_changed");
            }
        },
        commit_value: function() {
            this.change_datetime();
        },
    });

    instance.datetime_widget.DateWidgetCusto = instance.datetime_widget.DateTimeWidgetCusto.extend({
        jqueryui_object: 'datepicker',
        type_of_date: "date"
    });


    instance.datetime_widget.FieldDatetimeCusto = instance.web.form.AbstractField.extend(
        instance.web.form.ReinitializeFieldMixin, {

            template: "FieldDatetimeCusto",
            build_widget: function() {
                return new instance.datetime_widget.DateWidgetCusto(this);
            },
            destroy_content: function() {
                if (this.datewidget) {
                    this.datewidget.destroy();
                    this.datewidget = undefined;
                }
            },
            initialize_content: function() {
                var options = JSON.parse(this.node.attrs.options || '{}');

                var context = new instance.web.CompoundContext(
                    this.field_manager.dataset.get_context());
                context.add(this.build_context());
                context = context.eval();

                if ("minute_type" in options) {
                    this.minute_type = options["minute_type"]
                } else {
                    this.minute_type = "quarter"
                }
                
                if ("mindate" in context && context["mindate"]) {
                    if (typeof context["mindate"] == Date){
                        this.mindate = context["mindate"]
                    }
                    else{
                        this.mindate = instance.web.auto_str_to_date(context["mindate"], {
                            "widget": "date"
                        });
                    }
                }
                if ("maxdate" in context && context["maxdate"]) {
                    if (typeof context["maxdate"] == Date){
                        this.maxdate = context["maxdate"]
                    }
                    else{
                        this.maxdate = instance.web.auto_str_to_date(context["maxdate"], {
                            "widget": "date"
                        });
                    }
                }
                if ("ctx_mindate" in context && context["ctx_mindate"] && context["ctx_mindate"] in context && context[context["ctx_mindate"]]) {
                    if (typeof context[context["ctx_mindate"]] == Date){
                        this.maxdate = context[context["ctx_mindate"]]
                    }
                    else{
                        this.mindate = instance.web.auto_str_to_date(context[context["ctx_mindate"]], {
                            "widget": "date"
                        });
                    }
                }
                if ("ctx_maxdate" in context && context["ctx_maxdate"] && context["ctx_maxdate"] in context && context[context["ctx_maxdate"]]) {
                    if (typeof context[context["ctx_maxdate"]] == Date){
                        this.maxdate = context[context["ctx_maxdate"]]
                    }
                    else{
                        this.maxdate = instance.web.auto_str_to_date(context[context["ctx_maxdate"]], {
                            "widget": "date"
                        });
                    }
                }

                if (!this.get("effective_readonly")) {
                    this.datewidget = this.build_widget();
                    this.datewidget.on('datetime_changed', this, _.bind(function() {
                        this.internal_set_value(this.datewidget.get_value());
                    }, this));
                    this.datewidget.appendTo(this.$el);
                    this.setupFocus(this.datewidget.$input);
                }
            },
            render_value: function() {
                if (!this.get("effective_readonly")) {
                    this.datewidget.set_value(this.get('value'));
                } else {
                    this.$el.text(instance.web.format_value(this.get('value'), {
                        "widget": "datetime"
                    }, ''));
                }
            },
            is_syntax_valid: function() {
                if (!this.get("effective_readonly") && this.datewidget) {
                    return this.datewidget.is_valid_();
                }
                return true;
            },
            is_false: function() {
                return this.get('value') === '' || this._super();
            },
            focus: function() {
                var input = this.datewidget && this.datewidget.$input[0];
                return input ? input.focus() : false;
            },
            set_dimensions: function (height, width) {
                this._super(height, 270);
                if (!this.get("effective_readonly")) {
                    this.datewidget.$input.css('height', height);
                    this.$el.find("#datepicker_custo").css('width', 270);
                }
            }
        });

    instance.web.form.widgets.add(
        'datetime_custo', 'instance.datetime_widget.FieldDatetimeCusto');


};