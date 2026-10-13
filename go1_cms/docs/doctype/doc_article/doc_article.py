# Copyright (c) 2026, Go1 CMS and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from go1_cms.docs import render


class DocArticle(Document):
	def validate(self):
		self.title = (self.title or "").strip()
		self.slug = (self.slug or "").strip().lower() or render.slugify(self.title)
		if not render.is_slug(self.slug):
			frappe.throw(_("The slug may only use lower-case letters, digits and single dashes, such as get-started."))
		if frappe.db.exists("Doc Article", {"space": self.space, "slug": self.slug, "name": ["!=", self.name]}):
			frappe.throw(_("Another article in this space already uses the slug {0}.").format(self.slug))
		self._validate_parent()
		self._render()
		if self.status == "Published":
			if not (self.body_md or "").strip():
				frappe.throw(_("A published article needs a body."))
			if not self.published_on:
				self.published_on = now_datetime()

	def _validate_parent(self):
		if not self.parent_article:
			return
		if self.parent_article == self.name:
			frappe.throw(_("An article cannot be its own parent."))
		parent = frappe.db.get_value("Doc Article", self.parent_article, ["space", "parent_article"], as_dict=True)
		if not parent:
			frappe.throw(_("The parent article no longer exists."))
		if parent.space != self.space:
			frappe.throw(_("The parent article must be in the same space."))
		# One level of nesting keeps the sidebar readable; it also rules out cycles.
		if parent.parent_article:
			frappe.throw(_("Articles nest one level deep: the parent cannot itself have a parent."))
		if not self.is_new() and frappe.db.exists("Doc Article", {"parent_article": self.name}):
			frappe.throw(_("This article has articles under it, so it cannot be moved under another one."))

	def _render(self):
		out = render.render(self.body_md, self.space)
		self.body_html = out["html"]
		self.body_text = out["text"]
		self.outline_json = json.dumps(out["outline"])

	def on_update(self):
		from go1_cms.docs.api import clear_cache

		clear_cache()

	def on_trash(self):
		children = frappe.get_all("Doc Article", filters={"parent_article": self.name}, pluck="title")
		if children:
			frappe.throw(_("Move or delete the articles under this one first: {0}.").format(", ".join(children)))
		for space in frappe.get_all("Doc Space", filters={"default_article": self.name}, pluck="name"):
			frappe.db.set_value("Doc Space", space, "default_article", None)
		frappe.db.sql("update `tabProduct Feature` set doc_article=null where doc_article=%s", self.name)
		from go1_cms.docs.api import clear_cache

		clear_cache()
