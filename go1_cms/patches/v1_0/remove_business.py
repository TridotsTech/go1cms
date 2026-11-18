import frappe


def execute():
	"""The Business doctype is gone: drop its `business` Link field from every doctype that was stamped with it, then
	the doctypes themselves. (Web Page Builder and Proposal keep their own, older `business` Data field.)"""
	for name, dt in frappe.get_all("Custom Field", filters={"fieldname": "business", "options": "Business"}, fields=["name", "dt"], as_list=True):
		frappe.delete_doc("Custom Field", name, force=True, ignore_permissions=True)
		if frappe.db.has_column(dt, "business"):
			frappe.db.sql_ddl(f"alter table `tab{dt}` drop column `business`")
	for doctype in ("Business", "Business Domain"):
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True, ignore_missing=True)
		frappe.db.sql_ddl(f"drop table if exists `tab{doctype}`")   # deleting the DocType leaves its table behind
	frappe.cache.delete_value("go1_business_by_project")
	frappe.db.commit()
