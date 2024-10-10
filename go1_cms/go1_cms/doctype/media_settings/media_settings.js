// Copyright (c) 2020, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Media Settings', {
	refresh: function(frm) {
		if (frm.doc.__islocal) {
            if (has_common(frappe.user_roles, ['Vendor']) && frappe.session.user != 'Administrator') {
                frm.set_value('business', frappe.boot.sysdefaults.business)
            } else {
                frm.set_value('business', '')
            }
        }
         if (has_common(frappe.user_roles, ['Vendor']) && frappe.session.user != 'Administrator'){
            frm.set_df_property('business', 'hidden', 1)

         }
	}
});