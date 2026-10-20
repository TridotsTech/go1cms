# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Business(Document):
	def validate(self):
		seen = set()
		for row in self.get("domains") or []:
			row.domain = (row.domain or "").strip().lower().rstrip(".")
			if not row.domain:
				frappe.throw(_("A domain cannot be empty"))
			if row.domain in seen:
				frappe.throw(_("{0} is listed twice").format(row.domain))
			seen.add(row.domain)
			# A hostname answers for exactly one site.
			other = frappe.db.get_value(
				"Business Domain",
				{"domain": row.domain, "parenttype": "Business", "parent": ["!=", self.name or ""]},
				"parent",
			)
			if other:
				frappe.throw(_("{0} already belongs to {1}").format(row.domain, other))
		# only a verified (active) address can be the primary one: it is what a request resolves by
		live = [r for r in self.get("domains") or [] if r.status == "active"]
		primary = next((r for r in live if r.is_primary), None) or (live[0] if live else None)
		self.domain = primary.domain if primary else None

	def on_update(self):
		from go1_cms.go1_cms.business import clear_cache

		clear_cache()

	def on_trash(self):
		from go1_cms.go1_cms.business import clear_cache

		clear_cache()
