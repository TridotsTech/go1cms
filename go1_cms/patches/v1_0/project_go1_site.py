import frappe


def execute():
	"""Every existing CMS Project says which Go1 Site it lives on: this site (Safe to re-run)."""
	frappe.reload_doc("go1_cms", "doctype", "cms_project")
	if frappe.db.has_column("CMS Project", "go1_site"):
		frappe.db.sql("update `tabCMS Project` set go1_site = %s where ifnull(go1_site, '') = ''", frappe.local.site)
