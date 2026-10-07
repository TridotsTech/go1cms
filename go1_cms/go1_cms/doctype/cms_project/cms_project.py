# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CMSProject(Document):
	def before_insert(self):
		# Whoever creates a website owns it. System Managers see everything anyway.
		user = frappe.session.user
		if user in ("Administrator", "Guest") or "System Manager" in frappe.get_roles(user):
			return
		if not any(r.user == user for r in self.get("members") or []):
			self.append("members", {"user": user, "access": "Owner"})

	def after_insert(self):
		# A Panel Customer reaches pages through User Permissions (see
		# cms_frontend.panel_agent.permissions); give them one on the website they made.
		user = frappe.session.user
		roles = frappe.get_roles(user)
		if "Panel Customer" not in roles or "System Manager" in roles:
			return
		if not frappe.db.exists("User Permission", {"user": user, "allow": "CMS Project", "for_value": self.name}):
			frappe.get_doc({
				"doctype": "User Permission",
				"user": user,
				"allow": "CMS Project",
				"for_value": self.name,
				"apply_to_all_doctypes": 1,
			}).insert(ignore_permissions=True)
			frappe.cache.hdel("user_permissions", user)
