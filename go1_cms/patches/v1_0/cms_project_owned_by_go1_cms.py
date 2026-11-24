"""CMS Project was defined in both go1_cms and cms_frontend, so each migrate flipped its module to whichever app synced last.
go1_cms owns it now (the cms_frontend copy is removed); put the module back and reload the merged definition."""

import frappe


def execute():
	frappe.db.set_value("DocType", "CMS Project", "module", "Go1 CMS", update_modified=False)
	frappe.reload_doc("go1_cms", "doctype", "cms_project", force=True)
