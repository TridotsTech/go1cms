# Copyright (c) 2026, Go1 CMS and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from go1_cms.docs import render

# Words the /docs route uses itself; a space with one of these slugs would be unreachable.
RESERVED_SLUGS = {"search", "feed.xml", "features", "pricing", "assets", "api"}


class DocSpace(Document):
	def validate(self):
		self.slug = (self.slug or "").strip().lower() or render.slugify(self.title)
		if not render.is_slug(self.slug) or self.slug in RESERVED_SLUGS:
			frappe.throw(_("Choose another slug: lower-case letters, digits and dashes, and not one of {0}.").format(
				", ".join(sorted(RESERVED_SLUGS))))
		if self.default_article and frappe.db.get_value("Doc Article", self.default_article, "space") != self.name:
			frappe.throw(_("The default article must belong to this space."))
		if self.is_primary:
			# One primary space: short /docs/<article> addresses resolve against it.
			frappe.db.sql("update `tabDoc Space` set is_primary=0 where name!=%s", self.name)

	def on_update(self):
		from go1_cms.docs.api import clear_cache

		clear_cache()

	def on_trash(self):
		if frappe.db.exists("Doc Article", {"space": self.name}):
			frappe.throw(_("Delete or move the articles of this space first."))
		from go1_cms.docs.api import clear_cache

		clear_cache()
