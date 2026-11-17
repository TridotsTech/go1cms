"""Plan intake: what the control panel (go1saas) tells this site each website may do.

The panel pushes entitlements through `go1_cms.agent` / `go1_cms.plan` (see go1saas.bridge). They are kept in one
global value, `go1_cms_entitlements`:

    {"site": ..., "kind": "shared" | "site", "projects": {<project>: {...entitlements_for(tenant)}},
     "site_entitlements": {...}}            # only on a team's own site

Nothing here blocks anything by itself: `limits_for(project)` is the one place the builder and the API read limits from.
"""

import json

import frappe
from frappe import _

KEY = "go1_cms_entitlements"


def load():
	raw = frappe.db.get_global(KEY)
	try:
		return json.loads(raw) if raw else {}
	except ValueError:
		return {}


def save(data):
	frappe.db.set_global(KEY, json.dumps(data or {}))


def remember_project(project, entitlements):
	data = load()
	data.setdefault("kind", "shared")
	data.setdefault("projects", {})[project] = entitlements or {}
	save(data)


def for_project(project):
	return (load().get("projects") or {}).get(project)


def limits_for(project):
	"""The limits that apply to a website, or {} when the panel has told this site nothing (unlimited)."""
	return ((for_project(project) or {}).get("limits")) or {}


def set_entitlements(entitlements=None):
	"""Replace this site's entitlements with the panel's (entitlements_for_site)."""
	from go1_cms.agent import authorize

	authorize()
	if isinstance(entitlements, str):
		entitlements = json.loads(entitlements)
	if not isinstance(entitlements, dict):
		frappe.throw(_("entitlements must be an object"))
	save(entitlements)
	return {"ok": 1, "projects": sorted((entitlements.get("projects") or {}).keys())}


@frappe.whitelist(allow_guest=True)
def storage_usage(project=None, user=None):
	"""{"used_mb", "cap_mb"}: the owner's uploaded files against the website's storage limit (-1 = unlimited)."""
	from go1_cms.agent import authorize

	authorize()
	used = frappe.db.sql("select coalesce(sum(file_size), 0) from `tabFile` where owner=%s", user or "Administrator")[0][0] or 0
	return {"used_mb": round(used / 1048576, 2), "cap_mb": limits_for(project).get("storage_mb", -1)}
