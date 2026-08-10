# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt
"""Menu Builder API.

Reads and writes the `Menu` / `Menus Item` navigation tree.

Two things about the data model shape everything here:

1. `Menus Item.parent_menu` stores the parent's *label*, so renaming a label
   orphans its children and two siblings sharing a label are ambiguous. Rows
   now also carry `item_key` / `parent_key`, and the tree is read from those.
   `parent_menu` is still written on every save because the classic Jinja
   header and `api.get_header_info` join on it.
2. Rows are child-table rows. Echoing a row's `name` back on save keeps it in
   place; dropping the name deletes and re-inserts it.
"""

from __future__ import unicode_literals

import json
import re

import frappe
from frappe import _

MENU_TREE_CACHE_KEY = "go1_menu_tree"

MAX_MENU_DEPTH = 3
MAX_MEGA_COLUMNS = 4

MENU_ITEM_READ_FIELDS = [
	"name",
	"idx",
	"item_key",
	"parent_key",
	"parent_menu",
	"menu_label",
	"redirect_url",
	"link_target",
	"position",
	"icon",
	"is_mega_menu",
	"no_of_column",
	"mega_m_col_index",
	"is_visible",
	"badge",
	"css_class",
	"hide_on",
]

# Rendered straight into an href, so the scheme is an allowlist.
BLOCKED_URL_SCHEME = re.compile(r"^(javascript|data|vbscript)\s*:", re.IGNORECASE)
CONTROL_CHARS = re.compile(r"[\x00-\x20]")


# ──────────────────────────────────────────────────────────────────────────────
# Cache
# ──────────────────────────────────────────────────────────────────────────────

def clear_menu_tree_cache(menu_name=None):
	"""Drop one menu's cached tree, or the whole hash."""
	try:
		if menu_name:
			frappe.cache().hdel(MENU_TREE_CACHE_KEY, menu_name)
		else:
			frappe.cache().delete_key(MENU_TREE_CACHE_KEY)
	except Exception:
		# A cache that is down must never block a save.
		frappe.log_error(frappe.get_traceback(), "clear_menu_tree_cache")


# ──────────────────────────────────────────────────────────────────────────────
# Read
# ──────────────────────────────────────────────────────────────────────────────

def _legacy_node(node, depth):
	"""The exact key names and per-level field subset the classic SQL produced.

	Level 1 never selected `icon`; level 2 added `icon` and `mega_m_col_index`
	but dropped the mega-parent fields; level 3 carried neither. `header.html`
	branches on that, so the shape has to be reproduced field for field.

	Values come from the raw row, not the normalised node: the classic queries
	hand Jinja a bare `None` for an unset Data field, and coercing that to ""
	would be a behaviour change smuggled in under a parity flag.
	"""
	raw = node["_raw"]

	if depth == 0:
		out = frappe._dict({
			"menu_label": raw.get("menu_label"),
			"redirect_url": raw.get("redirect_url"),
			"is_mega_menu": raw.get("is_mega_menu"),
			"no_of_column": raw.get("no_of_column"),
		})
	elif depth == 1:
		out = frappe._dict({
			"menu_label": raw.get("menu_label"),
			"redirect_url": raw.get("redirect_url"),
			"icon": raw.get("icon"),
			"mega_m_col_index": raw.get("mega_m_col_index"),
		})
	else:
		out = frappe._dict({
			"menu_label": raw.get("menu_label"),
			"redirect_url": raw.get("redirect_url"),
			"icon": raw.get("icon"),
		})

	if depth < 2:
		out["child_menu"] = [_legacy_node(c, depth + 1) for c in node["children"]]
	return out


def _strip_raw(nodes):
	for node in nodes:
		node.pop("_raw", None)
		_strip_raw(node["children"])
	return nodes


def build_menu_tree(
	parent,
	parenttype="Menu",
	parentfield="menus",
	max_depth=MAX_MENU_DEPTH,
	legacy_keys=False,
	position=None,
	include_hidden=False,
):
	"""Assemble the nested tree for one `Menus Item` embed.

	One query plus an O(N) pass, against the classic path's 1 + N + N*M.
	Parameterised over the embed so `Header Component.top_menus` can adopt it
	without a second implementation.
	"""
	filters = {"parent": parent, "parenttype": parenttype, "parentfield": parentfield}
	if position:
		filters["position"] = position
	# Hiding is enforced here rather than in each renderer, so an item an author
	# switched off cannot reach a visitor through any consumer — FB2, the mobile
	# drawer or the classic Jinja header.
	if not include_hidden:
		filters["is_visible"] = 1

	rows = frappe.get_all(
		"Menus Item",
		filters=filters,
		fields=MENU_ITEM_READ_FIELDS,
		order_by="idx asc",
	)

	warnings = []
	nodes = {}
	by_key = {}
	by_label = {}

	for row in rows:
		key = row.get("item_key") or row.get("name")
		node = {
			"id": row.get("item_key") or "",
			"row": row.get("name"),
			"label": row.get("menu_label") or "",
			"url": row.get("redirect_url") or "",
			"target": row.get("link_target") or "",
			"icon": row.get("icon") or "",
			"position": row.get("position") or "",
			"is_mega_menu": int(row.get("is_mega_menu") or 0),
			"no_of_column": int(row.get("no_of_column") or 0),
			"mega_col": int(row.get("mega_m_col_index") or 0),
			"visible": int(row.get("is_visible") or 0),
			"badge": row.get("badge") or "",
			"cssClass": row.get("css_class") or "",
			"hideOn": [p.strip() for p in str(row.get("hide_on") or "").split(",") if p.strip()],
			"depth": 0,
			"children": [],
			"_raw": row,
		}
		nodes[key] = node
		by_key[key] = node
		# First-wins, matching the classic `WHERE parent_menu = %s` join.
		if node["label"] and node["label"] not in by_label:
			by_label[node["label"]] = node

	# parent_key wins; parent_menu is the fallback that keeps desk-grid edits
	# working, since the grid cannot write the read-only key fields.
	parent_of = {}
	for row in rows:
		key = row.get("item_key") or row.get("name")
		target = None
		if row.get("parent_key"):
			target = by_key.get(row.get("parent_key"))
		if target is None and row.get("parent_menu"):
			target = by_label.get(row.get("parent_menu"))
		if target is not None and target is not nodes[key]:
			parent_of[key] = target
		elif row.get("parent_menu") or row.get("parent_key"):
			# The row claims a parent that no longer exists — usually a label
			# that was renamed. It renders at the top level, which looks
			# deliberate, so say so rather than letting it pass silently.
			warnings.append(
				_("'{0}' pointed at a parent that no longer exists and now sits at the top level.").format(
					row.get("menu_label") or key
				)
			)

	roots = []
	for row in rows:
		key = row.get("item_key") or row.get("name")
		node = nodes[key]
		target = parent_of.get(key)

		# Walk up to a root, refusing cycles and over-deep chains.
		depth = 0
		seen = {key}
		cursor = target
		while cursor is not None:
			cursor_key = cursor["id"] or cursor["row"]
			if cursor_key in seen:
				warnings.append(
					_("'{0}' is nested inside itself and was moved to the top level.").format(node["label"])
				)
				target = None
				depth = 0
				break
			seen.add(cursor_key)
			depth += 1
			cursor = parent_of.get(cursor_key)

		if target is not None and depth >= max_depth:
			warnings.append(
				_("'{0}' is deeper than {1} levels and was dropped.").format(node["label"], max_depth)
			)
			continue

		node["depth"] = depth
		if target is None:
			roots.append(node)
		else:
			target["children"].append(node)

	if legacy_keys:
		return {"items": [_legacy_node(n, 0) for n in roots], "warnings": warnings}

	return {"items": _strip_raw(roots), "warnings": warnings}


@frappe.whitelist(allow_guest=True)
def get_menu_tree(menu=None, name=None, include_hidden=0):
	"""Public read for the FB2 renderer.

	Guest-safe because it never lists: a visitor can only name a menu that is
	already baked into a published page's layout, which they can read anyway.
	`get_menus` is the listing endpoint and stays behind auth.
	"""
	menu = menu or name
	if not menu:
		frappe.throw(_("menu is required"))

	# Editors ask for the hidden rows too; visitors never do. Only the visitor
	# shape is cached, so an editor session cannot poison the public payload.
	include_hidden = bool(frappe.utils.cint(include_hidden))
	if include_hidden:
		if not frappe.has_permission("Menu", "read", doc=menu):
			frappe.throw(_("Not permitted"), frappe.PermissionError)
		tree = build_menu_tree(menu, include_hidden=True)
		return {
			"menu": menu,
			"title": frappe.db.get_value("Menu", menu, "title") or menu,
			"items": tree["items"],
			"warnings": tree["warnings"],
			"version": str(frappe.db.get_value("Menu", menu, "modified") or ""),
		}

	cached = None
	try:
		cached = frappe.cache().hget(MENU_TREE_CACHE_KEY, menu)
	except Exception:
		cached = None
	if cached:
		return cached

	if not frappe.db.exists("Menu", menu):
		frappe.throw(_("Menu {0} not found").format(menu), frappe.DoesNotExistError)

	tree = build_menu_tree(menu)
	payload = {
		"menu": menu,
		"title": frappe.db.get_value("Menu", menu, "title") or menu,
		"items": tree["items"],
		"warnings": tree["warnings"],
		"version": str(frappe.db.get_value("Menu", menu, "modified") or ""),
	}

	try:
		frappe.cache().hset(MENU_TREE_CACHE_KEY, menu, payload)
	except Exception:
		pass

	return payload


@frappe.whitelist()
def get_menus():
	"""Menu list for the builder rail, with item counts."""
	menus = frappe.get_all(
		"Menu",
		fields=["name", "title", "modified"],
		order_by="title asc",
		limit_page_length=0,
	)

	counts = {}
	for row in frappe.db.sql(
		"""SELECT parent, COUNT(*) AS c FROM `tabMenus Item`
		   WHERE parenttype='Menu' AND parentfield='menus' GROUP BY parent""",
		as_dict=True,
	):
		counts[row.parent] = row.c

	for m in menus:
		m["item_count"] = counts.get(m["name"], 0)
		m["modified"] = str(m["modified"] or "")

	return menus


@frappe.whitelist()
def get_menu_link_targets(search=None, limit=200):
	"""Published pages for the link picker.

	Deliberately not `api.get_pages_list` — that one selects and JSON-parses
	`layout_json` and `draft_layout_json` per row to synthesise section lists,
	which is megabytes of payload to fill a dropdown needing two strings.
	"""
	filters = [["published", "=", 1], ["route", "!=", ""]]
	or_filters = None
	if search:
		or_filters = [
			["page_title", "like", "%{0}%".format(search)],
			["route", "like", "%{0}%".format(search)],
		]

	pages = frappe.get_all(
		"Web Page Builder",
		fields=["name", "page_title", "route", "published"],
		filters=filters,
		or_filters=or_filters,
		order_by="page_title asc",
		limit_page_length=frappe.utils.cint(limit) or 200,
	)

	return [
		{
			"name": p["name"],
			"title": p["page_title"] or p["route"],
			"route": p["route"],
			"published": p["published"],
		}
		for p in pages
	]


@frappe.whitelist()
def get_menu_usage(menu):
	"""Where a menu is referenced, including FB2 layouts.

	FB2 nav nodes hold the menu name as a plain string inside layout JSON, so
	Frappe's link integrity cannot see them: renaming or deleting a menu would
	silently break every bound nav. This is what makes that visible.
	"""
	if not menu:
		frappe.throw(_("menu is required"))

	page_sections = frappe.get_all(
		"Page Section",
		filters={"menu": menu},
		fields=["name", "section_title", "section_type"],
		limit_page_length=0,
	)

	header_components = frappe.get_all(
		"Header Component",
		filters={"menu": menu},
		fields=["name", "title"],
		limit_page_length=0,
	)

	pattern = "%{0}%".format(menu)
	fb2_pages = frappe.db.sql(
		"""SELECT name, page_title, route, published FROM `tabWeb Page Builder`
		   WHERE layout_json LIKE %(pat)s OR draft_layout_json LIKE %(pat)s
		   ORDER BY page_title ASC LIMIT 200""",
		{"pat": pattern},
		as_dict=True,
	)

	return {
		"page_sections": page_sections,
		"header_components": header_components,
		"fb2_pages": fb2_pages,
		"total": len(page_sections) + len(header_components) + len(fb2_pages),
	}


# ──────────────────────────────────────────────────────────────────────────────
# Write
# ──────────────────────────────────────────────────────────────────────────────

def _clean_url(value):
	if not value:
		return ""
	stripped = CONTROL_CHARS.sub("", str(value))
	if BLOCKED_URL_SCHEME.match(stripped):
		return None
	return str(value).strip()


def _validate_tree(tree, errors, warnings, labels, path=None, depth=0, parent=None):
	path = path or []
	if not isinstance(tree, list):
		errors.append(_("Menu items must be a list."))
		return

	for node in tree:
		if not isinstance(node, dict):
			errors.append(_("Menu items must be objects."))
			continue

		label = (node.get("label") or "").strip()
		here = path + [label or _("(untitled)")]
		trail = " › ".join(here)

		if not label:
			errors.append(_("{0}: every item needs a label.").format(trail))
		else:
			# Case-folded: the classic header joins children to parents with a SQL
			# `=` on the label, and MySQL's default collation is case-insensitive,
			# so "About Us" and "About us" collide there even though they look
			# distinct here.
			key = label.casefold()
			labels.setdefault(key, [0, label])
			labels[key][0] += 1

		if depth >= MAX_MENU_DEPTH:
			errors.append(_("{0}: menus support {1} levels.").format(trail, MAX_MENU_DEPTH))
			continue

		if _clean_url(node.get("url")) is None:
			errors.append(_("{0}: that link scheme is not allowed.").format(trail))

		is_mega = bool(node.get("is_mega_menu"))
		if is_mega and depth > 0:
			errors.append(_("{0}: only top-level items can be mega menus.").format(trail))

		if is_mega:
			cols = frappe.utils.cint(node.get("no_of_column") or 0)
			if cols < 1 or cols > MAX_MEGA_COLUMNS:
				errors.append(
					_("{0}: a mega menu needs between 1 and {1} columns.").format(trail, MAX_MEGA_COLUMNS)
				)

		if depth == 1 and parent and parent.get("is_mega_menu"):
			col = frappe.utils.cint(node.get("mega_col") or 0)
			parent_cols = frappe.utils.cint(parent.get("no_of_column") or 0)
			if col and parent_cols and col > parent_cols:
				errors.append(
					_("{0}: column {1} is beyond the parent's {2} columns.").format(trail, col, parent_cols)
				)

		children = node.get("children") or []
		if not children and not (node.get("url") or "").strip() and not is_mega:
			warnings.append(_("{0} has no link and no sub-items.").format(trail))

		_validate_tree(children, errors, warnings, labels, here, depth + 1, node)


def _flatten(tree, rows, known_rows, parent_label="", parent_key="", depth=0):
	"""Depth-first pre-order, so sibling order stays monotonic within a parent."""
	for node in tree:
		label = (node.get("label") or "").strip()
		item_key = (node.get("id") or "").strip() or frappe.generate_hash(length=12)
		is_mega = 1 if (depth == 0 and node.get("is_mega_menu")) else 0

		row = {
			"menu_label": label,
			"parent_menu": parent_label,
			"parent_key": parent_key,
			"item_key": item_key,
			"redirect_url": _clean_url(node.get("url")) or "",
			"link_target": node.get("target") or "",
			"icon": node.get("icon") or "",
			"position": (node.get("position") or "Left") if depth == 0 else "",
			"is_mega_menu": is_mega,
			"no_of_column": frappe.utils.cint(node.get("no_of_column")) if is_mega else 0,
			"mega_m_col_index": frappe.utils.cint(node.get("mega_col")) if depth == 1 else 0,
			# Absent means visible: a client that predates this field must not
			# silently hide every item it saves.
			"is_visible": 0 if node.get("visible") in (0, False, "0") else 1,
			"badge": (node.get("badge") or "").strip()[:24],
			"css_class": (node.get("cssClass") or "").strip()[:140],
			"hide_on": ",".join(
				d for d in ("desktop", "tablet", "mobile")
				if d in {str(x).strip().lower() for x in (node.get("hideOn") or [])}
			),
			"idx": len(rows) + 1,
		}

		# A submitted row name that does not already belong to this menu is
		# dropped rather than honoured, so a crafted payload cannot reparent
		# another menu's rows into this one.
		existing = node.get("row")
		if existing and existing in known_rows:
			row["name"] = existing

		rows.append(row)
		_flatten(node.get("children") or [], rows, known_rows, label, item_key, depth + 1)


@frappe.whitelist()
def save_menu_tree(menu=None, tree=None):
	"""Replace a menu's items with the submitted nested tree."""
	if not menu:
		frappe.throw(_("menu is required"))
	if not frappe.db.exists("Menu", menu):
		frappe.throw(_("Menu {0} not found").format(menu), frappe.DoesNotExistError)

	# has_permission, not a hardcoded role: the doctype's permission block is
	# the single source of truth, so a future grant actually takes effect.
	if not frappe.has_permission("Menu", "write", doc=menu):
		frappe.throw(_("Not permitted to edit this menu."), frappe.PermissionError)

	if isinstance(tree, str):
		tree = json.loads(tree)
	if tree is None:
		tree = []

	errors, warnings, labels = [], [], {}
	_validate_tree(tree, errors, warnings, labels)
	if errors:
		frappe.throw("<br>".join(errors), title=_("Menu cannot be saved"))

	# Duplicates warn rather than block: the new reader keys off parent_key and
	# is unaffected, and only the classic label join degrades — which it already
	# does for any such data that exists today.
	for count, label in labels.values():
		if count > 1:
			warnings.append(
				_("Two items are named '{0}' (labels are compared without case). "
				  "The classic theme's header nests by label and will attach sub-items to both.").format(label)
			)

	doc = frappe.get_doc("Menu", menu)
	known_rows = {r.name for r in (doc.menus or [])}

	rows = []
	_flatten(tree, rows, known_rows)

	doc.set("menus", [])
	for row in rows:
		doc.append("menus", row)
	doc.save()
	frappe.db.commit()

	fresh = build_menu_tree(menu, include_hidden=True)
	return {
		"menu": menu,
		"items": fresh["items"],
		"version": str(frappe.db.get_value("Menu", menu, "modified") or ""),
		"warnings": warnings + fresh["warnings"],
	}
