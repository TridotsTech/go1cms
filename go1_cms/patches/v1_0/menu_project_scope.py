"""MNU-01: give each existing menu the project that uses it.

A menu is only assigned when exactly one project's builder pages bind it AND the
classic theme (Header Component / Page Section) does not use it. Anything else
stays shared (project empty), which is exactly how every menu behaved before.
"""

import frappe


def execute():
	for menu in frappe.get_all("Menu", filters={"project": ("is", "not set")}, pluck="name"):
		if frappe.db.count("Header Component", {"menu": menu}) or frappe.db.count("Page Section", {"menu": menu}):
			continue
		needle = '%"menu": "{0}"%'.format(menu.replace("%", r"\%").replace("_", r"\_"))
		projects = frappe.db.sql(
			"""SELECT DISTINCT COALESCE(project, '') FROM `tabWeb Page Builder`
			   WHERE layout_json LIKE %(n)s OR draft_layout_json LIKE %(n)s""",
			{"n": needle},
		)
		projects = {p[0] for p in projects}
		if len(projects) == 1:
			project = projects.pop()
			if project and frappe.db.exists("CMS Project", project):
				frappe.db.set_value("Menu", menu, "project", project, update_modified=False)
