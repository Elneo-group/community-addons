/* @odoo-module */

import {ListRenderer} from "@web/views/list/list_renderer";
import {patch} from "@web/core/utils/patch";

patch(ListRenderer.prototype, {
    freezeColumnWidths() {
        const table = this.tableRef.el;
        const child_table = table.firstElementChild.firstElementChild;
        if (!$(child_table.firstChild).hasClass("o_list_row_count_sheliya")) {
            const a = $(child_table).prepend(
                '<th class="o_list_row_number_header o_list_row_count_sheliya row_no">'
            );
            a.find("th.o_list_row_count_sheliya").html("#");
        }
        return super.freezeColumnWidths();
    },
    getGroupNameCellColSpan(group) {
        let colspan = super.getGroupNameCellColSpan(group);
        return colspan + 1;
    },
});
