frappe.listview_settings['Executed Command'] = {
	add_fields: ["status"],
	get_indicator: function(doc) {
		if(doc.status == 'Success') {
			return [__("Success"), "green", "status,=,Success"];
		} else if(doc.status == 'Ongoing') {
			return [__("Ongoing"), "orange", "status,=,Ongoing"];
		} else {
			return [__("Failed"), "red", "status,=,Failed"];
		}
	}
};
