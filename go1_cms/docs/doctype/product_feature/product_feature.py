# Copyright (c) 2026, Go1 CMS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from go1_cms.docs import render


class ProductFeature(Document):
	def validate(self):
		self.slug = (self.slug or "").strip().lower() or render.slugify(self.title)
		if not render.is_slug(self.slug):
			frappe.throw(_("The slug may only use lower-case letters, digits and single dashes."))
		for plan in ("starter", "medium", "premium"):
			if not self.get(plan):
				self.set(plan + "_note", None)

	def on_update(self):
		from go1_cms.docs.api import clear_cache

		clear_cache()

	def on_trash(self):
		linked = frappe.db.sql(
			"""select a.title from `tabDoc Article Feature` f
			join `tabDoc Article` a on a.name = f.parent
			where f.feature = %s and a.status = 'Published'""",
			self.name,
			pluck=True,
		)
		if linked:
			frappe.throw(_("Published articles link this feature: {0}. Remove it from them first.").format(", ".join(linked)))
		from go1_cms.docs.api import clear_cache

		clear_cache()
