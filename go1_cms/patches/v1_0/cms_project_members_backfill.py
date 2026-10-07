"""SEC-05: give every existing website its members so nobody loses access.

The creator becomes Owner (unless it is Administrator or a System Manager, who see
everything), and every current Website Manager becomes an Editor of every website.
"""

import frappe


def execute():
	frappe.reload_doc("go1_cms", "doctype", "cms_project_member")
	frappe.reload_doc("go1_cms", "doctype", "cms_project")
	from go1_cms.go1_cms.cms_access import add_member

	managers = [
		u
		for u in frappe.get_all(
			"Has Role", filters={"role": "Website Manager", "parenttype": "User"}, pluck="parent", ignore_permissions=True
		)
		if u not in ("Administrator", "Guest")
		and frappe.db.get_value("User", u, "enabled")
		and "System Manager" not in frappe.get_roles(u)
	]
	for p in frappe.get_all("CMS Project", fields=["name", "owner"]):
		owner = p.owner
		if owner and owner not in ("Administrator", "Guest") and "System Manager" not in frappe.get_roles(owner):
			add_member(p.name, owner, "Owner")
		for u in managers:
			add_member(p.name, u, "Editor")
