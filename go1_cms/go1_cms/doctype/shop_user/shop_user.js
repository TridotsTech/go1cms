// Copyright (c) 2018, info@valiantsystems.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Shop User', {
	refresh: function(frm){
		if(has_common(frappe.user_roles,['Vendor']) && frappe.session.user!='Administrator'){
			frm.set_df_property('role','read_only',1)
			frm.set_df_property('role','hidden',1)
		}else{
			frm.set_df_property('role','hidden',0)
			frm.set_df_property('role','read_only',0)
		}
		frm.set_query("role", function() {
			return{
				"filters": {
					"name": ["in", ["Vendor", "Shipping Manager"]]
				}
			}
		});
		
	},
	after_save:function(frm){
		cur_frm.reload_doc();
	},
	restaurant: function(frm){
		if(!frm.doc.restaurant){
			frm.set_value('restaurant_name', '')
		}
	}
})