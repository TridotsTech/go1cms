# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt
"""Mark every existing `Menus Item` visible.

A Check field's default only applies to rows inserted after it exists; adding
the column leaves every current row at 0, which would hide every menu on every
site the moment the reader starts honouring the flag.
"""

import frappe


def execute():
	frappe.reload_doc("go1_cms", "doctype", "menus_item")

	# A blunt UPDATE is safe here precisely because patches run once — Frappe
	# records them in Patch Log — so a later migrate cannot un-hide an item an
	# author deliberately hid. Do NOT make this conditional-and-repeatable; that
	# is what would resurrect hidden items.
	frappe.db.sql(
		"""UPDATE `tabMenus Item` SET is_visible = 1
		   WHERE is_visible IS NULL OR is_visible = 0"""
	)
	frappe.db.commit()
