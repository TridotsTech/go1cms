// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Page Section', {
	refresh: function(frm) {
		if (frm.doc.layout_id) {
			frm.toggle_display([
				'reference_document',
				'condition',
				'choose_fields',
				'field_list',
				'sort_field',
				'sort_by',
				'display_data_randomly',
				'dynamic_section_section'
			], false);
			frm.toggle_display([
				'no_of_records',
				'dynamic_data'
			], true);
		} else {
			frm.toggle_display([
				'dynamic_data'
			], true);
		}
	}
});
