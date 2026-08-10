# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt
"""Give every `Menus Item` row a stable `item_key`, and translate the existing
label-based `parent_menu` links into `parent_key`.

Idempotent: both passes skip rows that already carry a value, so a repeated
migrate is a no-op. Covers `Menu.menus` and `Header Component.top_menus` alike,
since it iterates every row regardless of embed.
"""

import frappe


def execute():
	frappe.reload_doc("go1_cms", "doctype", "menus_item")

	_mint_item_keys()
	_resolve_parent_keys()

	frappe.db.commit()


def _mint_item_keys():
	rows = frappe.db.sql(
		"""SELECT name FROM `tabMenus Item`
		   WHERE item_key IS NULL OR item_key = ''
		   ORDER BY parent, parenttype, parentfield, idx""",
		as_dict=True,
	)
	for row in rows:
		# update_modified=False: a mechanical backfill must not read as a user
		# edit in the audit trail.
		frappe.db.set_value(
			"Menus Item", row.name, "item_key", frappe.generate_hash(length=12), update_modified=False
		)


def _resolve_parent_keys():
	rows = frappe.db.sql(
		"""SELECT name, parent, parenttype, parentfield, idx, menu_label, parent_menu, item_key
		   FROM `tabMenus Item`
		   ORDER BY parent, parenttype, parentfield, idx""",
		as_dict=True,
	)

	groups = {}
	for row in rows:
		groups.setdefault((row.parent, row.parenttype, row.parentfield), []).append(row)

	unresolved = []

	for group_rows in groups.values():
		# First-wins, matching the classic `WHERE parent_menu = %s` join.
		by_label = {}
		for row in group_rows:
			if row.menu_label and row.menu_label not in by_label:
				by_label[row.menu_label] = row.item_key

		for row in group_rows:
			if not row.parent_menu:
				continue
			existing = frappe.db.get_value("Menus Item", row.name, "parent_key")
			if existing:
				continue
			key = by_label.get(row.parent_menu)
			if key and key != row.item_key:
				frappe.db.set_value("Menus Item", row.name, "parent_key", key, update_modified=False)
			else:
				unresolved.append(
					"{0} (in {1}): parent_menu='{2}'".format(row.menu_label, row.parent, row.parent_menu)
				)

	if unresolved:
		# These rows were already orphaned before this patch ran; surface them
		# once rather than per row so the operator can see which menus are broken.
		frappe.log_error(
			"\n".join(unresolved),
			"backfill_menus_item_keys: unresolved parent_menu references",
		)
