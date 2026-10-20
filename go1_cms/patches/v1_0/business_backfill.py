import frappe


def execute():
	"""A Business for every CMS Project, the `business` field on every doctype that has a
	`project` field, and every existing row stamped. Safe to re-run."""
	frappe.reload_doc("go1_cms", "doctype", "business_domain")
	frappe.reload_doc("go1_cms", "doctype", "business")
	from go1_cms.go1_cms import business

	business.after_migrate()
	frappe.clear_cache()
