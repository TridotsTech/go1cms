# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from go1_cms.go1_cms.menu_api import clear_menu_tree_cache


class Menu(Document):
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
