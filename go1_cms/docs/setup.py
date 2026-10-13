"""Install-time setup for the docs: the Docs Editor role and the first content."""

import frappe

ROLE = "Docs Editor"


def ensure_role():
	"""The role the doctypes' permissions name. Runs before migrate as well, so a
	fresh site has it before the doctypes that reference it are synced."""
	if frappe.db.table_exists("Role") and not frappe.db.exists("Role", ROLE):
		frappe.get_doc({"doctype": "Role", "role_name": ROLE, "desk_access": 1}).insert(ignore_permissions=True)


def after_migrate():
	ensure_role()
	# First deploy only: a site with no space gets the seeded content. After that
	# the content belongs to the editors, and migrate never touches it.
	if frappe.db.table_exists("Doc Space") and not frappe.db.count("Doc Space"):
		from go1_cms.docs import seed

		try:
			seed.run()
		except Exception:
			frappe.log_error(frappe.get_traceback(), "go1_cms docs seed")
