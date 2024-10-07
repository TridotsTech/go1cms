frappe.treeview_settings["Business"] = {
	ignore_fields:["parent_business"],
	disable_add_node: true,
	toolbar: [
		{ toggle_btn: true },
		{
			label:__("Edit"),
			condition: function(node) {
				return !node.is_root;
			},
			click: function(node) {
				frappe.set_route("Form", "Business", node.data.value);
			}
		}
	]
}