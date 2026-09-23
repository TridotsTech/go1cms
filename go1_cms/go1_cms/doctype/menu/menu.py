# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from go1_cms.go1_cms.menu_api import clear_menu_tree_cache


class Menu(Document):
	def autoname(self):
		"""The title when it is free, otherwise the title plus a counter.

		Two projects may each have a "Main Menu", so the title can no longer be
		the name outright. The name is still readable because the classic Jinja
		header and every FB2 nav store it as a plain string.
		"""
		base = (self.title or "").strip() or _("Menu")
		name, n = base, 1
		while frappe.db.exists("Menu", name):
			n += 1
			name = f"{base} ({n})"
		self.name = name

	def validate(self):
		self.title = (self.title or "").strip()
		if not self.title:
			frappe.throw(_("A menu needs a name."))
		clash = frappe.db.get_value(
			"Menu",
			{"title": self.title, "project": self.project or ("is", "not set"), "name": ("!=", self.name)},
			"name",
		)
		if clash:
			where = _("this project") if self.project else _("the shared menus")
			frappe.throw(_("There is already a menu called '{0}' in {1}.").format(self.title, where))

	# Invalidation lives here rather than in hooks.py doc_events so it catches
	# every write path — the builder, the desk grid, patches, bench console,
	# data import — with no dependency on hook registration order.
	def on_update(self):
		clear_menu_tree_cache(self.name)

	def on_trash(self):
		clear_menu_tree_cache(self.name)

	def after_rename(self, old_name, new_name, merge=False):
		clear_menu_tree_cache(old_name)
		clear_menu_tree_cache(new_name)
