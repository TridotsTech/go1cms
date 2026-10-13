"""The docs API: the public /docs site, the /cms/docs admin, the feature catalogue.

Three kinds of callers:

Visitors (allow_guest; published rows only, explicit field lists, no doctype or
filter taken from the request)
    get_spaces, get_sidebar, get_article, search, vote, get_features, get_feature

Editors (System Manager or Docs Editor; the /cms/docs screen)
    docs_options, list_articles, get_article_for_edit, save_article,
    set_article_status, duplicate_article, delete_article, reorder_articles,
    preview_markdown, list_spaces, save_space, delete_space,
    list_features, save_feature, delete_feature, reorder_features

The www pages (go1_cms/www/docs.py, docs_feed.py) and the cms_frontend sitemap
hook use the plain functions `page_context`, `feed_items` and `sitemap_urls`.

Reads that every page view repeats (spaces, sidebars, features) are cached in
Redis under `go1_docs:` and dropped by `clear_cache`, which every Doc Space,
Doc Article and Product Feature save calls.
"""

import hashlib
import json

import frappe
from frappe import _
from frappe.utils import cint, now_datetime

from go1_cms.docs import render

EDITOR_ROLES = {"System Manager", "Docs Editor"}
CACHE_PREFIX = "go1_docs:"
CACHE_TTL = 6 * 3600
PLANS = ("starter", "medium", "premium")
CATEGORIES = ("Builder", "Panel", "Hosting", "Billing", "Team", "Integrations")
HIGHLIGHT_LIMIT = 8

ARTICLE_LIST_FIELDS = ["name", "title", "slug", "space", "status", "group_label", "parent_article", "sort_order",
                       "summary", "modified", "published_on"]
FEATURE_FIELDS = ["name", "title", "slug", "tagline", "description", "category", "status", "sort_order", "is_highlight",
                  "icon", "screenshot", "video_url", "doc_article", "starter", "starter_note", "medium", "medium_note",
                  "premium", "premium_note"]


# ── Access ────────────────────────────────────────────────────────────────────

def is_editor(user=None):
	user = user or frappe.session.user
	if not user or user == "Guest":
		return False
	return user == "Administrator" or bool(set(frappe.get_roles(user)) & EDITOR_ROLES)


def require_editor():
	if not is_editor():
		frappe.throw(_("You need the Docs Editor role for this."), frappe.PermissionError)


def require_system_manager():
	if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles():
		frappe.throw(_("Only a System Manager can do this."), frappe.PermissionError)


# ── Cache ─────────────────────────────────────────────────────────────────────

def clear_cache(*args, **kwargs):
	frappe.cache.delete_keys(CACHE_PREFIX)


def _cached(key, builder):
	full = CACHE_PREFIX + key
	hit = frappe.cache.get_value(full)
	if hit is not None:
		return hit
	value = builder()
	frappe.cache.set_value(full, value, expires_in_sec=CACHE_TTL)
	return value


def _parse(value, default=None):
	if value is None or value == "":
		return default
	if isinstance(value, (dict, list)):
		return value
	try:
		return json.loads(value)
	except ValueError:
		return default


# ── Visitors ──────────────────────────────────────────────────────────────────

def _published_spaces():
	def build():
		spaces = frappe.get_all(
			"Doc Space",
			filters={"is_published": 1},
			fields=["name", "title", "slug", "description", "icon", "sort_order", "is_primary", "default_article"],
			order_by="sort_order asc, title asc",
		)
		counts = dict(frappe.db.sql(
			"select space, count(*) from `tabDoc Article` where status='Published' group by space"))
		for s in spaces:
			s["article_count"] = counts.get(s.name, 0)
			s["route"] = "/docs/%s" % s.slug
		return spaces
	return _cached("spaces", build)


@frappe.whitelist(allow_guest=True)
def get_spaces():
	return _published_spaces()


def primary_space():
	spaces = _published_spaces()
	for s in spaces:
		if s.get("is_primary"):
			return s
	return spaces[0] if spaces else None


def _space_row(slug, drafts=False):
	row = frappe.db.get_value(
		"Doc Space", slug, ["name", "title", "slug", "description", "icon", "is_published", "is_primary", "default_article"],
		as_dict=True)
	if not row or (not row.is_published and not drafts):
		return None
	return row


def _sidebar(space, drafts=False):
	filters = {"space": space}
	if not drafts:
		filters["status"] = "Published"
	rows = frappe.get_all("Doc Article", filters=filters,
	                      fields=["name", "title", "slug", "status", "group_label", "parent_article", "sort_order"],
	                      order_by="sort_order asc, title asc")
	by_parent = {}
	for r in rows:
		r["route"] = render.article_route(space, r.slug)
		by_parent.setdefault(r.parent_article or "", []).append(r)
	names = {r.name for r in rows}
	groups, order = {}, []
	for r in by_parent.get("", []) + [r for r in rows if r.parent_article and r.parent_article not in names]:
		r["children"] = by_parent.get(r.name, [])
		label = r.group_label or ""
		if label not in groups:
			groups[label] = []
			order.append(label)
		groups[label].append(r)
	return [{"group": label, "items": groups[label]} for label in order]


@frappe.whitelist(allow_guest=True)
def get_sidebar(space, drafts=0):
	drafts = cint(drafts) and is_editor()
	if not _space_row(space, drafts):
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	if drafts:
		return _sidebar(space, True)
	return _cached("sidebar:%s" % space, lambda: _sidebar(space))


def _flat(sidebar):
	out = []
	for g in sidebar:
		for item in g["items"]:
			out.append(item)
			out.extend(item.get("children") or [])
	return out


def _features_for(article_name):
	names = frappe.get_all("Doc Article Feature", filters={"parent": article_name, "parenttype": "Doc Article"},
	                       pluck="feature", order_by="idx asc")
	if not names:
		return []
	rows = frappe.get_all("Product Feature", filters={"name": ["in", names], "status": ["!=", "Planned"]},
	                      fields=["name", "title", "slug", "tagline", "status", "icon"] + list(PLANS))
	order = {n: i for i, n in enumerate(names)}
	return sorted(rows, key=lambda r: order.get(r.name, 0))


def _article(space, slug, drafts=False):
	filters = {"space": space, "slug": slug}
	if not drafts:
		filters["status"] = "Published"
	name = frappe.db.get_value("Doc Article", filters, "name")
	if not name:
		return None
	doc = frappe.get_doc("Doc Article", name)
	sidebar = _sidebar(space, drafts)
	flat = _flat(sidebar)
	idx = next((i for i, r in enumerate(flat) if r.name == name), -1)
	prev_row = flat[idx - 1] if idx > 0 else None
	next_row = flat[idx + 1] if 0 <= idx < len(flat) - 1 else None
	parent = None
	if doc.parent_article:
		parent = frappe.db.get_value("Doc Article", doc.parent_article, ["title", "slug"], as_dict=True)
		if parent:
			parent["route"] = render.article_route(space, parent.slug)
	return {
		"name": doc.name, "title": doc.title, "slug": doc.slug, "space": space, "status": doc.status,
		"summary": doc.summary or "", "body_html": doc.body_html or "", "outline": _parse(doc.outline_json, []),
		"group_label": doc.group_label or "", "parent": parent,
		"route": render.article_route(space, doc.slug),
		"published_on": str(doc.published_on) if doc.published_on else None, "modified": str(doc.modified),
		"version_tag": doc.version_tag or "", "tags": [t.tag for t in doc.tags],
		"features": _features_for(doc.name),
		"helpful_yes": cint(doc.helpful_yes), "helpful_no": cint(doc.helpful_no),
		"prev": {"title": prev_row.title, "route": prev_row.route} if prev_row else None,
		"next": {"title": next_row.title, "route": next_row.route} if next_row else None,
		"sidebar": sidebar,
	}


@frappe.whitelist(allow_guest=True)
def get_article(space, slug, drafts=0):
	drafts = bool(cint(drafts)) and is_editor()
	if not _space_row(space, drafts):
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	art = _article(space, slug, drafts)
	if not art:
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	return art


def _snippet(text, q, width=180):
	text = text or ""
	low = text.lower()
	pos = low.find(q.lower()) if q else -1
	if pos < 0:
		return text[:width] + ("…" if len(text) > width else "")
	start = max(0, pos - width // 3)
	out = text[start:start + width]
	return ("…" if start else "") + out + ("…" if start + width < len(text) else "")


@frappe.whitelist(allow_guest=True)
def search(q, space=None, limit=20):
	"""Title matches first, then summary, then body. A LIKE query is plenty for a
	few hundred articles; the signature stays when it moves to full-text search."""
	q = (q or "").strip()[:100]
	if len(q) < 2:
		return []
	limit = min(max(cint(limit) or 20, 1), 50)
	like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
	conditions = ["a.status='Published'", "s.is_published=1",
	              "(a.title like %(like)s or a.summary like %(like)s or a.body_text like %(like)s)"]
	params = {"like": like, "limit": limit}
	if space:
		conditions.append("a.space=%(space)s")
		params["space"] = space
	rows = frappe.db.sql(
		"""select a.title, a.slug, a.space, a.summary, a.body_text, s.title as space_title,
			case when a.title like %(like)s then 0 when a.summary like %(like)s then 1 else 2 end as rank_
		from `tabDoc Article` a join `tabDoc Space` s on s.name = a.space
		where {}
		order by rank_ asc, a.sort_order asc, a.title asc
		limit %(limit)s""".format(" and ".join(conditions)),
		params, as_dict=True)
	return [{
		"title": r.title, "space": r.space, "space_title": r.space_title, "slug": r.slug,
		"route": render.article_route(r.space, r.slug),
		"snippet": _snippet(r.summary if r.rank_ < 2 and r.summary else r.body_text, q),
	} for r in rows]


@frappe.whitelist(allow_guest=True, methods=["POST"])
def vote(space, slug, helpful):
	"""One vote per visitor per article per day (keyed on the address the request came
	from); the page also remembers the vote in the browser so the buttons stay answered."""
	name = frappe.db.get_value("Doc Article", {"space": space, "slug": slug, "status": "Published"}, "name")
	if not name:
		frappe.throw(_("Not found"), frappe.DoesNotExistError)
	who = hashlib.sha1(("%s|%s" % (frappe.local.request_ip or "", name)).encode()).hexdigest()[:20]
	key = CACHE_PREFIX + "vote:" + who
	field = "helpful_yes" if cint(helpful) else "helpful_no"
	if not frappe.cache.get_value(key):
		frappe.cache.set_value(key, 1, expires_in_sec=24 * 3600)
		frappe.db.sql("update `tabDoc Article` set `{0}` = ifnull(`{0}`, 0) + 1 where name=%s".format(field), name)
	yes, no = frappe.db.get_value("Doc Article", name, ["helpful_yes", "helpful_no"])
	return {"helpful_yes": cint(yes), "helpful_no": cint(no)}


def _feature_row(r):
	r = dict(r)
	r["route"] = "/docs/features/%s" % r["slug"]
	r["plans"] = [{"plan": p, "label": p.title(), "included": bool(r.get(p)), "note": r.get(p + "_note") or ""} for p in PLANS]
	return r


def _all_features():
	def build():
		rows = frappe.get_all("Product Feature", fields=FEATURE_FIELDS, order_by="sort_order asc, title asc")
		articles = {}
		names = [r.doc_article for r in rows if r.doc_article]
		if names:
			for a in frappe.get_all("Doc Article", filters={"name": ["in", names], "status": "Published"},
			                        fields=["name", "title", "slug", "space"]):
				articles[a.name] = {"title": a.title, "route": render.article_route(a.space, a.slug)}
		out = []
		for r in rows:
			row = _feature_row(r)
			row["article"] = articles.get(r.doc_article)
			row.pop("doc_article", None)
			out.append(row)
		return out
	return _cached("features", build)


@frappe.whitelist(allow_guest=True)
def get_features(category=None, plan=None, highlight=0, include_planned=0):
	"""Live and Beta features in catalogue order; Planned ones only on request (the roadmap view)."""
	rows = _all_features()
	if not cint(include_planned):
		rows = [r for r in rows if r["status"] != "Planned"]
	if category:
		rows = [r for r in rows if r["category"] == category]
	if plan in PLANS:
		rows = [r for r in rows if r.get(plan)]
	if cint(highlight):
		rows = [r for r in rows if r.get("is_highlight")][:HIGHLIGHT_LIMIT]
	return sorted(rows, key=lambda r: (CATEGORIES.index(r["category"]) if r["category"] in CATEGORIES else 99,
	                                   r.get("sort_order") or 0, r["title"]))


@frappe.whitelist(allow_guest=True)
def get_feature(slug):
	for r in _all_features():
		if r["slug"] == slug and (r["status"] != "Planned" or is_editor()):
			return r
	frappe.throw(_("Not found"), frappe.DoesNotExistError)


# ── The www pages ─────────────────────────────────────────────────────────────

def page_context(path, query=None):
	"""Everything www/docs.html needs for one /docs address, or None for a 404.

	    /docs                          landing: spaces + highlighted features
	    /docs/search?q=                search results
	    /docs/features[/<slug>]        the feature catalogue and one feature
	    /docs/pricing                  the plan comparison grid
	    /docs/<space>                  the space's default (or first) article
	    /docs/<space>/<slug>           an article
	    /docs/<slug>                   an article of the primary space (the
	                                   addresses the product site linked to)
	"""
	query = query or {}
	editor = is_editor()
	parts = [p for p in (path or "").strip("/").split("/") if p]
	base = {"spaces": _published_spaces(), "is_editor": editor, "primary": primary_space()}

	if not parts:
		return dict(base, view="landing", highlights=get_features(highlight=1))
	head = parts[0]
	if head == "search" and len(parts) == 1:
		q = (query.get("q") or "").strip()
		space = query.get("space") or None
		return dict(base, view="search", q=q, space_filter=space, results=search(q, space) if q else [])
	if head == "features":
		if len(parts) == 1:
			planned = bool(cint(query.get("roadmap")))
			return dict(base, view="features", features=get_features(include_planned=planned), roadmap=planned,
			            categories=CATEGORIES)
		if len(parts) == 2:
			try:
				return dict(base, view="feature", feature=get_feature(parts[1]))
			except frappe.DoesNotExistError:
				return None
		return None
	if head == "pricing" and len(parts) == 1:
		return dict(base, view="pricing", features=get_features(), categories=CATEGORIES, plans=PLANS)

	space = _space_row(head, editor)
	if space:
		if len(parts) == 1:
			slug = None
			if space.default_article:
				slug = frappe.db.get_value("Doc Article", space.default_article, "slug")
			if not slug:
				flat = _flat(_sidebar(space.name, editor))
				slug = flat[0].slug if flat else None
			if not slug:
				return dict(base, view="empty_space", space=space)
			return dict(base, view="redirect", location=render.article_route(space.name, slug))
		if len(parts) == 2:
			art = _article(space.name, parts[1], editor)
			return dict(base, view="article", space=space, article=art) if art else None
		return None

	if len(parts) == 1 and base["primary"]:
		prim = base["primary"]
		art = _article(prim["name"], head, editor)
		if art:
			return dict(base, view="article", space=_space_row(prim["name"], editor), article=art,
			            canonical=art["route"])
	return None


def feed_items(limit=30):
	rows = frappe.db.sql(
		"""select a.title, a.slug, a.space, a.summary, a.published_on, a.modified
		from `tabDoc Article` a join `tabDoc Space` s on s.name = a.space
		where a.status='Published' and s.is_published=1
		order by coalesce(a.published_on, a.modified) desc limit %s""", limit, as_dict=True)
	for r in rows:
		r["route"] = render.article_route(r.space, r.slug)
	return rows


def sitemap_urls():
	"""cms_sitemap_urls hook: every published article, space and showcase page."""
	out = [{"route": "docs", "title": "Docs"}, {"route": "docs/features", "title": "Features"},
	       {"route": "docs/pricing", "title": "Pricing"}]
	for r in frappe.db.sql(
		"""select a.title, a.slug, a.space, a.modified from `tabDoc Article` a
		join `tabDoc Space` s on s.name = a.space where a.status='Published' and s.is_published=1""", as_dict=True):
		out.append({"route": render.article_route(r.space, r.slug).strip("/"), "title": r.title,
		            "lastmod": str(r.modified)[:10]})
	for f in get_features():
		out.append({"route": f["route"].strip("/"), "title": f["title"]})
	return out


# ── Editors: articles ─────────────────────────────────────────────────────────

@frappe.whitelist()
def docs_options():
	"""What the editor's pickers offer."""
	require_editor()
	return {
		"spaces": frappe.get_all("Doc Space", fields=["name", "title", "slug", "is_published", "is_primary",
		                                              "default_article", "description", "icon", "sort_order"],
		                         order_by="sort_order asc, title asc"),
		"tags": frappe.get_all("Doc Tag", pluck="name", order_by="name asc"),
		"features": frappe.get_all("Product Feature", fields=["name", "title", "category", "status"],
		                           order_by="category asc, sort_order asc"),
		"categories": list(CATEGORIES),
		"can_manage_spaces": frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(),
	}


@frappe.whitelist()
def list_articles(space=None, status=None, q=None):
	require_editor()
	filters = {}
	if space:
		filters["space"] = space
	if status in ("Draft", "Published"):
		filters["status"] = status
	or_filters = None
	if q:
		like = "%%%s%%" % q.strip()
		or_filters = [["title", "like", like], ["slug", "like", like], ["summary", "like", like]]
	return frappe.get_all("Doc Article", filters=filters, or_filters=or_filters, fields=ARTICLE_LIST_FIELDS,
	                      order_by="sort_order asc, title asc", limit_page_length=1000)


def _edit_payload(doc):
	return {
		"name": doc.name, "title": doc.title, "slug": doc.slug, "space": doc.space, "status": doc.status,
		"group_label": doc.group_label or "", "parent_article": doc.parent_article or "",
		"sort_order": cint(doc.sort_order), "summary": doc.summary or "", "body_md": doc.body_md or "",
		"body_html": doc.body_html or "", "version_tag": doc.version_tag or "",
		"tags": [t.tag for t in doc.tags], "features": [f.feature for f in doc.features],
		"published_on": str(doc.published_on) if doc.published_on else None,
		"helpful_yes": cint(doc.helpful_yes), "helpful_no": cint(doc.helpful_no),
		"modified": str(doc.modified), "route": render.article_route(doc.space, doc.slug),
	}


@frappe.whitelist()
def get_article_for_edit(name):
	require_editor()
	return _edit_payload(frappe.get_doc("Doc Article", name))


def _ensure_tags(tags):
	out = []
	for t in tags or []:
		t = (t or "").strip().lower()[:60]
		if not t or t in out:
			continue
		if not frappe.db.exists("Doc Tag", t):
			frappe.get_doc({"doctype": "Doc Tag", "tag": t}).insert(ignore_permissions=True)
		out.append(t)
	return out


ARTICLE_EDITABLE = ("title", "slug", "space", "group_label", "parent_article", "sort_order", "summary", "body_md",
                    "version_tag", "status")


@frappe.whitelist()
def save_article(data, name=None, expected_modified=None):
	"""Create or update one article. `expected_modified` is the `modified` the editor
	opened; when the row has moved on since, nothing is written and the answer says so."""
	require_editor()
	data = _parse(data, {}) or {}
	if name:
		doc = frappe.get_doc("Doc Article", name)
		if expected_modified and str(doc.modified) != str(expected_modified):
			return {"status": "conflict", "modified_by": doc.modified_by, "modified": str(doc.modified)}
	else:
		doc = frappe.new_doc("Doc Article")
		doc.status = "Draft"
	for key in ARTICLE_EDITABLE:
		if key in data:
			doc.set(key, data[key] if data[key] != "" or key in ("summary", "body_md", "group_label") else None)
	if "tags" in data:
		doc.set("tags", [{"tag": t} for t in _ensure_tags(data["tags"])])
	if "features" in data:
		doc.set("features", [{"feature": f} for f in (data["features"] or []) if frappe.db.exists("Product Feature", f)])
	doc.save()
	return {"status": "saved", "article": _edit_payload(doc)}


@frappe.whitelist()
def set_article_status(name, status):
	require_editor()
	if status not in ("Draft", "Published"):
		frappe.throw(_("Unknown status."))
	doc = frappe.get_doc("Doc Article", name)
	doc.status = status
	doc.save()
	return _edit_payload(doc)


@frappe.whitelist()
def duplicate_article(name):
	require_editor()
	src = frappe.get_doc("Doc Article", name)
	copy = frappe.copy_doc(src)
	copy.title = "%s (copy)" % src.title
	base = (src.slug + "-copy")[:74]
	slug, n = base, 2
	while frappe.db.exists("Doc Article", {"space": src.space, "slug": slug}):
		slug = "%s-%d" % (base, n)
		n += 1
	copy.slug = slug
	copy.status = "Draft"
	copy.published_on = None
	copy.helpful_yes = copy.helpful_no = 0
	copy.sort_order = cint(src.sort_order) + 1
	copy.insert()
	return _edit_payload(copy)


@frappe.whitelist()
def delete_article(name):
	require_editor()
	frappe.delete_doc("Doc Article", name)
	return {"ok": True}


@frappe.whitelist()
def reorder_articles(space, items):
	"""One call per drag: [{name, parent_article, group_label, sort_order}] for the moved rows."""
	require_editor()
	items = _parse(items, []) or []
	for it in items:
		doc = frappe.get_doc("Doc Article", it["name"])
		if doc.space != space:
			frappe.throw(_("{0} is not in this space.").format(doc.title))
		doc.parent_article = it.get("parent_article") or None
		if "group_label" in it:
			doc.group_label = it.get("group_label") or ""
		doc.sort_order = cint(it.get("sort_order"))
		doc.save()
	return _sidebar(space, True)


@frappe.whitelist()
def preview_markdown(body_md, space=None):
	require_editor()
	out = render.render(body_md, space)
	return {"html": out["html"], "outline": out["outline"]}


# ── Editors: spaces ───────────────────────────────────────────────────────────

SPACE_EDITABLE = ("title", "slug", "description", "icon", "sort_order", "is_published", "is_primary", "default_article")


@frappe.whitelist()
def save_space(data, name=None):
	require_editor()
	data = _parse(data, {}) or {}
	if name:
		doc = frappe.get_doc("Doc Space", name)
		if data.get("slug") and data["slug"] != name:
			frappe.throw(_("A space's slug cannot change once it is created; its addresses are already shared."))
	else:
		doc = frappe.new_doc("Doc Space")
	for key in SPACE_EDITABLE:
		if key in data and not (name and key == "slug"):
			doc.set(key, data[key] if data[key] != "" else None)
	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def delete_space(name):
	require_system_manager()
	frappe.delete_doc("Doc Space", name)
	return {"ok": True}


# ── Editors: features ─────────────────────────────────────────────────────────

FEATURE_EDITABLE = [f for f in FEATURE_FIELDS if f != "name"]


@frappe.whitelist()
def list_features():
	require_editor()
	rows = frappe.get_all("Product Feature", fields=FEATURE_FIELDS + ["modified"], order_by="sort_order asc, title asc")
	return {"features": rows, "categories": list(CATEGORIES), "highlight_limit": HIGHLIGHT_LIMIT}


@frappe.whitelist()
def save_feature(data, name=None):
	require_editor()
	data = _parse(data, {}) or {}
	if name:
		doc = frappe.get_doc("Product Feature", name)
		if data.get("slug") and data["slug"] != name:
			frappe.throw(_("A feature's slug cannot change once it is created."))
	else:
		doc = frappe.new_doc("Product Feature")
	for key in FEATURE_EDITABLE:
		if key in data and not (name and key == "slug"):
			doc.set(key, data[key] if data[key] != "" else None)
	doc.save()
	highlights = frappe.db.count("Product Feature", {"is_highlight": 1})
	return {"feature": doc.as_dict(), "highlight_count": highlights,
	        "warning": _("{0} features are highlighted; the landing shows the first {1}.").format(highlights, HIGHLIGHT_LIMIT)
	        if highlights > HIGHLIGHT_LIMIT else None}


@frappe.whitelist()
def delete_feature(name):
	require_editor()
	frappe.delete_doc("Product Feature", name)
	return {"ok": True}


@frappe.whitelist()
def reorder_features(category, names):
	require_editor()
	names = _parse(names, []) or []
	for i, n in enumerate(names):
		if frappe.db.get_value("Product Feature", n, "category") != category:
			frappe.throw(_("{0} is not in {1}.").format(n, category))
		frappe.db.set_value("Product Feature", n, "sort_order", (i + 1) * 10)
	clear_cache()
	return {"ok": True}


@frappe.whitelist()
def seed_docs(reset=0):
	require_system_manager()
	from go1_cms.docs import seed

	return seed.run(reset=cint(reset))
