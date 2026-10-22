# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt
"""Business: one record per site, the single key every site-scoped row hangs off.

It lives here, in go1_cms, because the rows it keys live on the customer sites, which run
go1_cms and cms_frontend but not the panel app. go1_cpanel only keeps a Business in step with
its Tenant and Project Domains (go1_cpanel/business.py).

Up to ~50 sites share one database, so "the data of acme.nvi.frappe.cloud" has to be
one indexed lookup, not a scan of every project. A Business is created for each CMS
Project (name = the project name), holds the site's domains, and is stamped onto every
doctype that has a `project` field as a `business` Link (a Custom Field, indexed).

    business_for_host("acme.nvi.frappe.cloud")   -> {"business": ..., "project": ...}
    get_site_data("acme.nvi.frappe.cloud", "Web Page Builder", fields=["name", "route"])
"""

import frappe
from frappe import _

CACHE_KEY = "go1_business_by_project"

# Never given a `business` field: the keys themselves, the panel's own bookkeeping.
EXCLUDE = {"Business", "Business Domain", "CMS Project", "CMS Project Member", "Tenant", "Shared Site", "Project Domain"}


def clear_cache():
	frappe.cache.delete_value(CACHE_KEY)


# ── project ⇄ business ───────────────────────────────────────────────────────

def business_for_project(project):
	"""Name of the Business that owns `project` (cached), or None."""
	if not project:
		return None
	hit = frappe.cache.hget(CACHE_KEY, project)
	if hit:
		return hit
	name = frappe.db.get_value("Business", {"project": project}, "name")
	if name:
		frappe.cache.hset(CACHE_KEY, project, name)
	return name


def _status_for(project):
	return "Archived" if frappe.db.get_value("CMS Project", project, "status") == "Archived" else "Active"


def ensure_business(project):
	"""Create (or refresh) the Business for a CMS Project. Idempotent."""
	if not project or not frappe.db.exists("CMS Project", project):
		return None
	name = frappe.db.get_value("Business", {"project": project}, "name")
	status = _status_for(project)
	if name:
		# Archiving a project archives its site; un-archiving brings it back. A Suspended
		# business (set by the panel) is left alone by a project save.
		current = frappe.db.get_value("Business", name, "status")
		if status == "Archived" and current != "Archived":
			frappe.db.set_value("Business", name, "status", "Archived")
		elif status == "Active" and current == "Archived":
			frappe.db.set_value("Business", name, "status", "Active")
		return name
	doc = frappe.get_doc({"doctype": "Business", "business_name": project, "project": project, "status": status})
	doc.insert(ignore_permissions=True)
	return doc.name


def on_project_save(doc, method=None):
	"""doc_events for CMS Project (after_insert / on_update)."""
	if not frappe.db.table_exists("Business"):  # before the first migrate has created it
		return
	ensure_business(doc.name)


def on_project_trash(doc, method=None):
	name = frappe.db.get_value("Business", {"project": doc.name}, "name")
	if name:
		frappe.delete_doc("Business", name, ignore_permissions=True, force=True)


# ── domains ──────────────────────────────────────────────────────────────────

def upsert_domain(project, host, domain_type="custom_domain", primary=False, status="active", remove=False):
	"""Record (or drop) one hostname on the project's Business."""
	host = (host or "").strip().lower().rstrip(".")
	name = ensure_business(project)
	if not name or not host:
		return None
	doc = frappe.get_doc("Business", name)
	rows = [r for r in doc.domains if r.domain == host]
	if remove:
		if not rows:
			return name
		doc.domains = [r for r in doc.domains if r.domain != host]
	else:
		row = rows[0] if rows else doc.append("domains", {"domain": host})
		row.domain_type = domain_type
		row.status = status
		if primary:
			for r in doc.domains:
				r.is_primary = 1 if r.domain == host else 0
		elif not any(r.is_primary for r in doc.domains if r.status != "removed"):
			row.is_primary = 1
	doc.save(ignore_permissions=True)
	return name


PANEL_STATUS = {"suspended": "Suspended", "archived": "Archived", "active": "Active", "over_quota": "Active"}


def set_status(project, panel_status):
	"""The panel's tenant status (active / over_quota / suspended / archived) on the Business."""
	name = ensure_business(project)
	status = PANEL_STATUS.get((panel_status or "").lower())
	if name and status and frappe.db.get_value("Business", name, "status") != status:
		frappe.db.set_value("Business", name, "status", status)
		clear_cache()
	return name


def business_for_host(host):
	"""{"business", "project", "domain"} for a hostname (platform subdomain or custom
	domain), or None. One indexed lookup."""
	host = (host or "").split(":")[0].strip().lower().rstrip(".")
	if not host:
		return None
	parent = frappe.db.get_value(
		"Business Domain", {"domain": host, "parenttype": "Business", "status": "active"}, "parent"
	) or frappe.db.get_value("Business", {"domain": host}, "name")
	if not parent:
		return None
	project = frappe.db.get_value("Business", parent, "project")
	return {"business": parent, "project": project, "domain": host}


# ── the field every site-scoped doctype gets ─────────────────────────────────

CMS_APPS = ("go1_cms", "cms_frontend")


def scoped_doctypes():
	"""The CMS apps' doctypes that have a `project` field (a CMS Project name), minus the
	keys themselves. Other apps are never touched: ERPNext's own `project` fields point at
	its Project doctype, and its ledgers must not grow a column for this."""
	modules = frappe.get_all("Module Def", filters={"app_name": ["in", CMS_APPS]}, pluck="name")
	if not modules:
		return []
	names = frappe.get_all(
		"DocField",
		filters={"parenttype": "DocType", "fieldname": "project", "fieldtype": ["in", ["Link", "Data"]]},
		pluck="parent",
	)
	names = set(names)
	out = []
	for dt in sorted(names - EXCLUDE):
		row = frappe.db.get_value("DocType", dt, ["module", "istable", "issingle", "is_virtual"], as_dict=True)
		if not row or row.module not in modules or row.istable or row.issingle or row.is_virtual:
			continue
		out.append(dt)
	return out


def ensure_fields():
	"""Add the indexed `business` Link to every scoped doctype that lacks one."""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	fields = {}
	for dt in scoped_doctypes():
		if frappe.get_meta(dt).has_field("business"):
			continue
		fields[dt] = [
			{
				"fieldname": "business",
				"fieldtype": "Link",
				"options": "Business",
				"label": "Site (Business)",
				"insert_after": "project",
				"read_only": 1,
				"search_index": 1,
				"no_copy": 0,
			}
		]
	if fields:
		create_custom_fields(fields, update=False)
	return sorted(fields)


def reconcile():
	"""Stamp `business` on rows that have a project but no business yet (rows written by
	raw SQL, or before a project had its Business). Returns {doctype: rows_fixed}."""
	fixed = {}
	for dt in scoped_doctypes():
		if not frappe.get_meta(dt).has_field("business"):
			continue
		table = f"`tab{dt}`"
		todo = frappe.db.sql(
			f"select count(*) from {table} where ifnull(project,'') != '' and ifnull(business,'') = ''"
		)[0][0]
		if not todo:
			continue
		frappe.db.sql(
			f"""update {table} t inner join `tabBusiness` b on b.project = t.project
			set t.business = b.name where ifnull(t.project,'') != '' and ifnull(t.business,'') = ''"""
		)
		left = frappe.db.sql(
			f"select count(*) from {table} where ifnull(project,'') != '' and ifnull(business,'') = ''"
		)[0][0]
		if todo - left:  # rows still left name a project that no longer exists
			fixed[dt] = todo - left
	return fixed


def stamp(doc, method=None):
	"""doc_events '*' / before_save: a row that names a project also names its business."""
	if doc.doctype in EXCLUDE:
		return
	project = doc.get("project")
	if not project or not doc.meta.has_field("business"):
		return
	business = business_for_project(project)
	if business and doc.get("business") != business:
		doc.business = business


def after_migrate():
	"""Every migrate: a Business for each project, the field on each scoped doctype,
	and any stray rows stamped. Idempotent and cheap once everything is in place."""
	if not frappe.db.table_exists("Business") or not frappe.db.table_exists("CMS Project"):
		return
	for project in frappe.get_all("CMS Project", pluck="name"):
		ensure_business(project)
	ensure_fields()
	reconcile()


# ── fetch a site's data by its domain ────────────────────────────────────────

def _may_use(project):
	user = frappe.session.user
	if user == "Administrator" or "System Manager" in frappe.get_roles(user):
		return True
	return bool(frappe.db.exists("CMS Project Member", {"parent": project, "user": user}))


@frappe.whitelist()
def list_site_doctypes():
	"""Doctypes whose rows can be fetched by domain."""
	return [dt for dt in scoped_doctypes() if frappe.get_meta(dt).has_field("business")]


@frappe.whitelist()
def get_site_data(domain, doctype, fields=None, filters=None, limit=50, order_by=None):
	"""Rows of `doctype` that belong to the site served at `domain`.

	    get_site_data("acme.nvi.frappe.cloud", "Web Page Builder", ["name", "route"])

	The caller must be a System Manager or a member of that site."""
	hit = business_for_host(domain)
	if not hit:
		frappe.throw(_("No site answers on {0}").format(domain), frappe.DoesNotExistError)
	if not _may_use(hit["project"]):
		frappe.throw(_("You do not have access to {0}").format(domain), frappe.PermissionError)
	if not frappe.get_meta(doctype).has_field("business"):
		frappe.throw(_("{0} is not scoped to a site").format(doctype))
	fields = frappe.parse_json(fields) if isinstance(fields, str) else fields
	filters = frappe.parse_json(filters) if isinstance(filters, str) else filters
	if filters is not None and not isinstance(filters, dict):
		frappe.throw(_("filters must be an object"))
	return frappe.get_all(
		doctype,
		fields=fields or ["name"],
		filters={**(filters or {}), "business": hit["business"]},
		order_by=order_by or "modified desc",
		limit_page_length=min(int(limit or 50), 500),
	)
