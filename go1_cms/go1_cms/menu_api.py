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
	"description",
	"css_class",
	"active_paths",
	"hide_on",
	"auto_source",
	"auto_path",
	"auto_limit",
]

# MNU-03: items that fill their own sub-items at render time.
AUTO_SOURCES = ("project_pages", "path", "blog_posts")
AUTO_DEFAULT_LIMIT = 8
AUTO_MAX_LIMIT = 20

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


def _auto_of(row):
	source = (row.get("auto_source") or "").strip()
	if source not in AUTO_SOURCES:
		return None
	return {
		"source": source,
		"path": (row.get("auto_path") or "").strip(),
		"limit": frappe.utils.cint(row.get("auto_limit")) or AUTO_DEFAULT_LIMIT,
	}


def _short_title(title):
	"""'Krishko — About Us' → 'About Us': generated pages carry a site prefix."""
	title = (title or "").strip()
	return title.split(" — ")[-1].strip() if " — " in title else title


def auto_items(auto, project):
	"""[{label, url}] for one automatic item. Never raises: a bad rule just
	yields nothing, the rest of the menu still renders."""
	try:
		source = auto.get("source")
		limit = max(1, min(AUTO_MAX_LIMIT, frappe.utils.cint(auto.get("limit")) or AUTO_DEFAULT_LIMIT))

		if source == "blog_posts":
			if not frappe.db.exists("DocType", "Blog Post"):
				return []
			rows = frappe.get_all(
				"Blog Post",
				filters={"published": 1},
				fields=["title", "route"],
				order_by="published_on desc, creation desc",
				limit_page_length=limit,
			)
			return [{"label": r.title, "url": "/" + (r.route or "").strip("/")} for r in rows if r.route]

		filters = {"published": 1, "route": ("is", "set")}
		if project:
			filters["project"] = project
		elif source == "project_pages":
			return []  # a shared menu has no project to list

		if source == "path":
			prefix = (auto.get("path") or "").strip().rstrip("*").strip("/")
			if not prefix:
				return []
			like = prefix.replace("%", r"\%").replace("_", r"\_") + "/_%"
			rows = frappe.db.sql(
				"""SELECT page_title, route FROM `tabWeb Page Builder`
				   WHERE published = 1 AND (route LIKE %(a)s OR route LIKE %(b)s)
				   {project} ORDER BY creation ASC LIMIT %(n)s""".format(
					project="AND project = %(p)s" if project else ""
				),
				{"a": like, "b": "/" + like, "p": project, "n": limit},
				as_dict=True,
			)
		else:
			rows = frappe.get_all(
				"Web Page Builder",
				filters=filters,
				fields=["page_title", "route"],
				order_by="creation asc",
				limit_page_length=limit,
			)
		return [
			{"label": _short_title(r.page_title) or r.route, "url": "/" + (r.route or "").strip().strip("/")}
			for r in rows
		]
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Menu automatic items")
		return []


def _expand_auto(nodes, project, max_depth):
	for node in nodes:
		auto = node.get("auto")
		if auto and node["depth"] + 1 < max_depth:
			node["children"] = [
				{
					"id": "", "row": "", "label": it["label"], "url": it["url"], "target": "",
					"icon": "", "position": "", "is_mega_menu": 0, "no_of_column": 0, "mega_col": 0,
					"visible": 1, "badge": "", "description": "", "cssClass": "", "activePaths": [],
					"hideOn": list(node.get("hideOn") or []), "auto": None,
					"depth": node["depth"] + 1, "children": [], "generated": 1,
				}
				for it in auto_items(auto, project)
			]
		else:
			_expand_auto(node["children"], project, max_depth)


def clear_auto_menus(doc=None, method=None):
	"""Pages or blog posts changed: menus with automatic items are stale.

	Only when such an item exists — most sites have none, and the public tree
	cache should not be thrown away on every page save for nothing.
	"""
	try:
		if frappe.db.exists("Menus Item", {"parenttype": "Menu", "auto_source": ("is", "set")}):
			clear_menu_tree_cache()
	except Exception:
		pass


@frappe.whitelist()
def preview_auto_items(menu=None, source=None, path=None, limit=None):
	"""What an automatic item would show right now — for the editor."""
	_require_menu_perm("read")
	project = frappe.db.get_value("Menu", menu, "project") if menu else ""
	return auto_items({"source": source, "path": path, "limit": limit}, project or "")


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
	expand_auto=None,
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
			"description": row.get("description") or "",
			"cssClass": row.get("css_class") or "",
			# Extra paths that also count as "this item's page" — a blog post
			# keeping the Blog tab lit, say. Split here so every renderer gets a
			# list and none of them has to know the storage format.
			"activePaths": [
				p.strip() for p in re.split(r"[,\n]", str(row.get("active_paths") or "")) if p.strip()
			],
			"hideOn": [p.strip() for p in str(row.get("hide_on") or "").split(",") if p.strip()],
			"auto": _auto_of(row),
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

	# Visitors get automatic items filled in; the editor (include_hidden) sees
	# the rule, never the generated rows — or saving would freeze them in.
	if expand_auto is None:
		expand_auto = not include_hidden
	if expand_auto and parenttype == "Menu":
		_expand_auto(roots, frappe.db.get_value("Menu", parent, "project") or "", max_depth)

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
def get_menus(project=None):
	"""Menu list for the builder rail and the FB2 menu picker, with item counts.

	With `project`, only that project's menus plus the shared ones (no project)
	come back — the set a page in that project may bind. Without it, every menu,
	for the admin view.
	"""
	filters = None
	or_filters = None
	if project:
		or_filters = [["project", "=", project], ["project", "is", "not set"]]

	menus = frappe.get_all(
		"Menu",
		fields=["name", "title", "project", "modified"],
		filters=filters,
		or_filters=or_filters,
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

	names = {}
	project_ids = {m["project"] for m in menus if m.get("project")}
	if project_ids:
		for p in frappe.get_all(
			"CMS Project", filters={"name": ("in", list(project_ids))}, fields=["name", "project_name"]
		):
			names[p.name] = p.project_name or p.name

	for m in menus:
		m["title"] = m.get("title") or m["name"]
		m["project"] = m.get("project") or ""
		m["project_name"] = names.get(m["project"], m["project"])
		m["item_count"] = counts.get(m["name"], 0)
		m["modified"] = str(m["modified"] or "")

	return menus


def _require_menu_perm(ptype, menu=None):
	if not frappe.has_permission("Menu", ptype, doc=menu):
		frappe.throw(_("Not permitted."), frappe.PermissionError)


def _clean_project(project):
	project = (project or "").strip()
	if project and not frappe.db.exists("CMS Project", project):
		frappe.throw(_("Project {0} not found").format(project), frappe.DoesNotExistError)
	return project


@frappe.whitelist()
def create_menu(title=None, project=None):
	"""New empty menu in a project (or shared when `project` is empty)."""
	_require_menu_perm("create")
	doc = frappe.get_doc({
		"doctype": "Menu",
		"title": (title or "").strip(),
		"project": _clean_project(project),
		"is_static_menu": 0,
	})
	doc.insert()
	frappe.db.commit()
	return {"name": doc.name, "title": doc.title, "project": doc.project or ""}


@frappe.whitelist()
def rename_menu(menu=None, title=None):
	"""Change the label only.

	The document name is deliberately left alone: FB2 navs and the classic
	header store it as a plain string, so renaming the document used to break
	every page that bound the menu.
	"""
	if not menu or not frappe.db.exists("Menu", menu):
		frappe.throw(_("Menu {0} not found").format(menu), frappe.DoesNotExistError)
	_require_menu_perm("write", menu)
	doc = frappe.get_doc("Menu", menu)
	doc.title = (title or "").strip()
	doc.save()
	frappe.db.commit()
	return {"name": doc.name, "title": doc.title}


@frappe.whitelist()
def set_menu_project(menu=None, project=None):
	"""Move a menu into a project, or make it shared (empty `project`)."""
	if not menu or not frappe.db.exists("Menu", menu):
		frappe.throw(_("Menu {0} not found").format(menu), frappe.DoesNotExistError)
	_require_menu_perm("write", menu)
	doc = frappe.get_doc("Menu", menu)
	doc.project = _clean_project(project)
	doc.save()
	frappe.db.commit()

	# Pages of OTHER projects that bind it now point at a menu their project
	# cannot see; they still render (the name is unchanged) but the author
	# should know.
	others = []
	if doc.project:
		needle = '%"menu": "{0}"%'.format(menu.replace("%", r"\%").replace("_", r"\_"))
		others = frappe.db.sql(
			"""SELECT name, page_title, project FROM `tabWeb Page Builder`
			   WHERE (layout_json LIKE %(n)s OR draft_layout_json LIKE %(n)s)
			   AND COALESCE(project, '') != %(p)s LIMIT 50""",
			{"n": needle, "p": doc.project},
			as_dict=True,
		)
	return {"name": doc.name, "project": doc.project or "", "other_project_pages": others}


@frappe.whitelist()
def get_menu_link_targets(search=None, limit=200, project=None):
	"""Published pages for the link picker.

	Deliberately not `api.get_pages_list` — that one selects and JSON-parses
	`layout_json` and `draft_layout_json` per row to synthesise section lists,
	which is megabytes of payload to fill a dropdown needing two strings.
	"""
	filters = [["published", "=", 1], ["route", "!=", ""]]
	# A menu that belongs to a project links to that project's pages; a shared
	# menu (no project) may point anywhere.
	if project:
		filters.append(["project", "=", project])
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
# Link health (MNU-02)
# ──────────────────────────────────────────────────────────────────────────────
#
# A menu link is only a string, so deleting, unpublishing or re-routing a page
# left menus pointing at nothing, silently. The check below mirrors how the
# published site itself decides a path is real (www/frontend.py + WEB-01's
# not_found): a Web Page Builder route, a detail page served by its parent
# route, a Frappe www page, or a website-generator document (Blog Post, Web
# Form, ...). Anything else would be a 404 for the visitor.

EXTERNAL_URL = re.compile(r"^([a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def _path_of(url):
	return (url or "").split("#", 1)[0].split("?", 1)[0].strip()


def _page_index():
	index = {}
	for r in frappe.get_all(
		"Web Page Builder",
		fields=["name", "page_title", "route", "published", "project"],
		limit_page_length=0,
	):
		key = (r.route or "").strip().strip("/")
		index.setdefault(key, []).append(r)
	return index


def _framework_route(clean):
	"""A path Frappe itself serves: a www page or a web-view document."""
	try:
		from frappe.website.router import get_pages

		if clean in get_pages():
			return True
	except Exception:
		pass
	try:
		from frappe.website.page_renderers.document_page import _find_matching_document_webview
		from frappe.website.router import get_page_info_from_web_page_with_dynamic_routes

		if _find_matching_document_webview(clean) or get_page_info_from_web_page_with_dynamic_routes(clean):
			return True
	except Exception:
		pass
	return False


def _link_status(url, index, project):
	raw = (url or "").strip()
	if not raw or raw.startswith("#") or "{{" in raw:
		return {"status": "skip"}
	if EXTERNAL_URL.match(raw):
		return {"status": "external"}

	path = _path_of(raw)
	clean = path.strip("/")
	if not clean:
		return {"status": "ok", "page": _("Home")}

	try:
		from cms_frontend import not_found as nf

		if nf.is_reserved("/" + clean):
			return {"status": "ok"}
	except Exception:
		pass

	def pick(rows):
		# The menu's own project first, then anything published.
		rows = sorted(rows, key=lambda r: (not r.published, (r.project or "") != (project or "")))
		return rows[0]

	rows = index.get(clean)
	if rows:
		row = pick(rows)
		title = row.page_title or row.name
		if not row.published:
			return {"status": "unpublished", "page": title,
			        "message": _("'{0}' is not published — visitors get a 404.").format(title)}
		if project and row.project and row.project != project:
			return {"status": "other_project", "page": title,
			        "message": _("'{0}' belongs to another project.").format(title)}
		return {"status": "ok", "page": title}

	# Detail pages: /services/<slug> is served by the page at /services.
	parts = clean.split("/")
	while len(parts) > 1:
		parts = parts[:-1]
		for row in index.get("/".join(parts), []):
			if row.published:
				return {"status": "ok", "page": row.page_title or row.name}

	if _framework_route(clean):
		return {"status": "ok"}

	return {"status": "missing", "message": _("No page lives at {0} — visitors get a 404.").format("/" + clean)}


@frappe.whitelist()
def check_menu_links(urls=None, project=None):
	"""{url: {status, page?, message?}} for the builder's warnings.

	status: ok | unpublished | missing | other_project | external | skip
	"""
	_require_menu_perm("read")
	if isinstance(urls, str):
		urls = json.loads(urls or "[]")
	urls = [str(u) for u in (urls or [])][:500]
	index = _page_index()
	return {u: _link_status(u, index, project or "") for u in dict.fromkeys(urls)}


def follow_page_route_change(doc, method=None):
	"""Web Page Builder on_update: when a page's route changes, move every menu
	link that pointed at the old address to the new one.

	Only exact links move (a query string or #anchor after the path is kept),
	and only in menus of the page's own project or shared menus — another
	project's identically-named route is not this page.
	"""
	before = doc.get_doc_before_save()
	if not before:
		return
	old = (before.route or "").strip().strip("/")
	new = (doc.route or "").strip().strip("/")
	if not old or old == new:
		return

	rows = frappe.db.sql(
		"""SELECT mi.name, mi.parent, mi.redirect_url, m.project
		   FROM `tabMenus Item` mi JOIN `tabMenu` m ON m.name = mi.parent
		   WHERE mi.parenttype = 'Menu' AND mi.redirect_url IN %(cands)s""",
		{"cands": tuple({"/" + old, old, "/" + old + "/"})},
		as_dict=True,
	)
	# Suffixed forms (?tab=x, #team) need a LIKE, kept separate so the common
	# case stays an index lookup.
	for pre in ("/" + old, old):
		rows += frappe.db.sql(
			"""SELECT mi.name, mi.parent, mi.redirect_url, m.project
			   FROM `tabMenus Item` mi JOIN `tabMenu` m ON m.name = mi.parent
			   WHERE mi.parenttype = 'Menu'
			   AND (mi.redirect_url LIKE %(q)s OR mi.redirect_url LIKE %(h)s)""",
			{"q": pre.replace("%", r"\%").replace("_", r"\_") + "?%",
			 "h": pre.replace("%", r"\%").replace("_", r"\_") + "#%"},
			as_dict=True,
		)

	touched = set()
	seen = set()
	for r in rows:
		if r.name in seen:
			continue
		seen.add(r.name)
		if r.project and doc.project and r.project != doc.project:
			continue
		url = r.redirect_url or ""
		path = _path_of(url)
		suffix = url[len(path):]
		lead = "/" if path.startswith("/") else ""
		frappe.db.set_value("Menus Item", r.name, "redirect_url", lead + new + suffix, update_modified=False)
		touched.add(r.parent)

	for menu in touched:
		clear_menu_tree_cache(menu)


# ──────────────────────────────────────────────────────────────────────────────
# AI suggestion (MNU-05)
# ──────────────────────────────────────────────────────────────────────────────

SUGGEST_MAX_PAGES = 150


def _suggest_prompt(project_name, menu_title, pages):
	listing = "\n".join("- {0} → /{1}".format(p["title"], p["route"]) for p in pages)
	return (
		"You are organising a website's navigation menu.\n"
		f"Website: {project_name}\n"
		f"Menu being built: {menu_title or 'Main menu'}\n\n"
		"These are the site's published pages (title → address):\n"
		f"{listing}\n\n"
		"Design a clear menu from them:\n"
		"- At most 7 top-level items. Home first if there is a home page, Contact last if there is one.\n"
		"- Group related pages under a parent (e.g. every service page under \"Services\"). A parent may "
		"link to an overview page or have no link at all. Never more than 3 levels.\n"
		"- Short labels, 1-3 words, in the same language as the page titles. Drop repeated site names "
		"or prefixes from titles (\"Acme — About Us\" becomes \"About Us\").\n"
		"- Leave out pages that do not belong in a main menu: legal pages, thank-you or confirmation pages, "
		"404 pages, and detail pages of a list (one blog post, one product) when their list page exists.\n"
		"- Only use addresses from the list above, copied exactly.\n\n"
		"Reply with ONLY this JSON, nothing else:\n"
		'{"items": [{"label": "", "url": "/address-or-empty", "children": [ ...same shape... ]}]}'
	)


@frappe.whitelist()
def suggest_menu(project=None, title=None, attempt=0):
	"""Draft a menu from a project's published pages.

	Returns {"outline": "<indented text>", "dropped": n} for the builder's
	"Edit as a list" dialog — the author reviews and edits it there; nothing is
	written here. Every link the model returns is checked against the page list,
	so an invented address cannot reach the menu.
	"""
	_require_menu_perm("write")
	project = _clean_project(project)
	if not project:
		frappe.throw(_("Pick a project first — the suggestion is built from its pages."))

	rows = frappe.get_all(
		"Web Page Builder",
		filters={"project": project, "published": 1, "route": ("is", "set")},
		fields=["page_title", "route"],
		order_by="creation asc",
		limit_page_length=SUGGEST_MAX_PAGES,
	)
	pages = [{"title": r.page_title or r.route, "route": (r.route or "").strip().strip("/")} for r in rows]
	if not pages:
		frappe.throw(_("This project has no published pages to build a menu from."))

	allowed = {"/" + p["route"] for p in pages} | {"/"}
	project_name = frappe.db.get_value("CMS Project", project, "project_name") or project

	from cms_frontend import ai_transport
	from cms_frontend.stream_parse import loads_lenient

	try:
		content, _model, _msg = ai_transport.chat(
			[{"role": "user", "content": _suggest_prompt(project_name, title, pages)}],
			model=ai_transport.resolve_model("build"),
			max_tokens=3000,
			# A second "Suggest again" should not return the same menu.
			temperature=0.3 if not frappe.utils.cint(attempt) else 0.8,
			timeout=90,
		)
	except frappe.ValidationError:
		raise  # usage limits / permission (AIC-02) already speak plainly
	except Exception as e:
		# AiTransportError carries a readable reason (out of credits, rate
		# limited, no key); anything else must not leak a traceback.
		if type(e).__name__ == "AiTransportError":
			frappe.throw(str(e), title=_("AI suggestion failed"))
		frappe.log_error(frappe.get_traceback(), "Menu AI suggestion")
		frappe.throw(_("The AI could not be reached. Try again in a moment."), title=_("AI suggestion failed"))
	text = str(content or "").strip()
	if text.startswith("```"):
		text = text.strip("`").split("\n", 1)[-1].rsplit("```", 1)[0]
	data, err = loads_lenient(text[text.find("{"): text.rfind("}") + 1])
	if err or not isinstance(data, dict):
		frappe.throw(_("The AI's answer could not be read. Try again."))

	dropped = 0
	lines = []

	def emit(nodes, depth):
		nonlocal dropped
		for n in (nodes or [])[:40]:
			if not isinstance(n, dict):
				continue
			label = re.sub(r"\s+", " ", str(n.get("label") or "")).strip().replace("|", "/")[:60]
			if not label:
				continue
			url = str(n.get("url") or "").strip()
			if url and not url.startswith("/"):
				url = "/" + url
			url = url.rstrip("/") or ("/" if url else "")
			if url and url not in allowed:
				dropped += 1
				url = ""
			lines.append("  " * depth + label + (f" | {url}" if url else ""))
			if depth < MAX_MENU_DEPTH - 1:
				emit(n.get("children"), depth + 1)

	emit(data.get("items"), 0)
	return {"outline": "\n".join(lines), "dropped": dropped, "pages": len(pages)}


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
		auto = node.get("auto") if isinstance(node.get("auto"), dict) else None
		if auto and auto.get("source"):
			if depth >= MAX_MENU_DEPTH - 1:
				errors.append(_("{0}: an automatic item needs room for sub-items — move it up a level.").format(trail))
			if children:
				errors.append(_("{0}: an automatic item fills its own sub-items — remove the ones added by hand.").format(trail))
			if auto.get("source") == "path" and not (auto.get("path") or "").strip():
				errors.append(_("{0}: say which address the pages sit under.").format(trail))
			continue
		if not children and not (node.get("url") or "").strip() and not is_mega:
			warnings.append(_("{0} has no link and no sub-items.").format(trail))

		_validate_tree(children, errors, warnings, labels, here, depth + 1, node)


def _keep_if_absent(node, key, existing_row, fieldname, computed):
	"""`computed`, unless the client never sent `key` and the row already has a value."""
	if key in node or existing_row is None:
		return computed
	return existing_row.get(fieldname) or computed


def _auto_fields(node, existing_row, depth):
	"""An absent `auto` key (a client from before MNU-03) keeps the stored rule."""
	if "auto" not in node and existing_row is not None:
		return {
			"auto_source": existing_row.get("auto_source") or "",
			"auto_path": existing_row.get("auto_path") or "",
			"auto_limit": existing_row.get("auto_limit") or 0,
		}
	auto = node.get("auto") or {}
	source = auto.get("source") if isinstance(auto, dict) else None
	if source not in AUTO_SOURCES or depth >= MAX_MENU_DEPTH - 1:
		return {"auto_source": "", "auto_path": "", "auto_limit": 0}
	path = (auto.get("path") or "").strip()[:200] if source == "path" else ""
	if BLOCKED_URL_SCHEME.match(path):
		path = ""
	return {
		"auto_source": source,
		"auto_path": path,
		"auto_limit": max(0, min(AUTO_MAX_LIMIT, frappe.utils.cint(auto.get("limit")))),
	}


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
			# Same carry-forward rule as active_paths: a client that predates
			# the field says nothing about it, and that must not wipe it.
			"description": _keep_if_absent(
				node, "description", known_rows.get(node.get("row")), "description",
				re.sub(r"\s+", " ", str(node.get("description") or "")).strip()[:160],
			),
			"css_class": (node.get("cssClass") or "").strip()[:140],
			# Patterns only ever feed a client-side string compare, so the one
			# thing worth enforcing is that nothing here can become an href.
			#
			# A node that omits the key entirely came from a client built before
			# the field existed — a browser tab left open across the deploy — and
			# an omission there means "I don't know about this", not "clear it".
			# An empty list is a real instruction and does clear it.
			"active_paths": _keep_if_absent(
				node, "activePaths", known_rows.get(node.get("row")), "active_paths",
				",".join(
					p for p in (
						str(x).strip()[:200] for x in (node.get("activePaths") or [])
					) if p and not BLOCKED_URL_SCHEME.match(p)
				)[:1000],
			),
			**_auto_fields(node, known_rows.get(node.get("row")), depth),
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
	# name -> the row as it stands, so a save can both reject foreign row names
	# and carry forward fields the submitting client never knew about.
	known_rows = {r.name: r for r in (doc.menus or [])}

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
