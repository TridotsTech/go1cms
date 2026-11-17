"""Customer-site agent: the endpoints the control panel (go1saas) calls on a site that hosts websites.

Every endpoint takes the site's panel secret (site_config `go1saas_secret`) in the `X-Go1-Panel-Secret` header. When the panel
and the site are one and the same bench (a dev bench) go1saas.bridge calls these functions in process and sets
`frappe.flags.panel_bridge_local`, which stands in for the header.

Endpoints (go1saas.bridge.METHODS): ping, create_project, bootstrap, set_entitlements (go1_cms.plan), set_project_status,
set_domain, set_default_project, project_preview, site_projects, clear_cache, storage_usage, set_frontend_stack, adopt_owner_password.
Login links: `sso` (+ `verify_token`).
"""

import hmac
import json

import frappe
from frappe import _

from go1_cms import plan

STATUS_MAP = {"active": "Published", "published": "Published", "draft": "Draft", "in progress": "In Progress",
	"suspended": "Draft", "inactive": "Draft", "over_quota": "Draft", "archived": "Archived"}
DOMAINS_KEY = "go1_cms_domains"
DEFAULT_KEY = "go1_cms_default_project"


# ── access ───────────────────────────────────────────────────────────────────

def authorize():
	"""Allow the in-process bridge, or a request carrying this site's panel secret."""
	if frappe.flags.get("panel_bridge_local"):
		return
	expected = frappe.conf.get("go1saas_secret") or ""
	given = (frappe.get_request_header("X-Go1-Panel-Secret") or "") if getattr(frappe.local, "request", None) else ""
	if not expected or not hmac.compare_digest(expected, given):
		frappe.throw(_("Bad panel secret"), frappe.AuthenticationError)


def _version():
	from go1_cms import __version__

	return __version__


def _project(name):
	if not name or not frappe.db.exists("CMS Project", name):
		frappe.throw(_("Unknown project {0}").format(name))
	return frappe.get_doc("CMS Project", name)




# ── endpoints ────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def ping():
	authorize()
	return {"ok": 1, "app_version": _version(), "site": frappe.local.site}


def _unique_name(base):
	name, n = base, 1
	while frappe.db.exists("CMS Project", name):
		n += 1
		name = f"{base} {n}"
	return name


def _ensure_user(email, full_name=None, password_hash=None):
	if not email:
		return None
	if not frappe.db.exists("User", email):
		user = frappe.get_doc({"doctype": "User", "email": email, "first_name": (full_name or email.split("@")[0]), "send_welcome_email": 0,
			"enabled": 1, "user_type": "Website User"})
		user.flags.ignore_permissions = True
		user.insert()
	if password_hash and not frappe.db.sql("select 1 from `__Auth` where doctype='User' and name=%s and fieldname='password'", email):
		_set_password_hash(email, password_hash)
	return email


def _set_password_hash(email, password_hash):
	frappe.db.sql("""insert into `__Auth` (doctype, name, fieldname, password, encrypted) values ('User', %s, 'password', %s, 0)
		on duplicate key update password=%s""", (email, password_hash, password_hash))


@frappe.whitelist(allow_guest=True)
def create_project(project_name, subdomain, owner_email=None, owner_name=None, entitlements=None, frontend_stack="vue"):
	"""A new website (CMS Project) with its owner as a member; answers {"project", "slug", "site_url", "app_version"}."""
	authorize()
	if isinstance(entitlements, str):
		entitlements = json.loads(entitlements or "{}")
	slug = (subdomain or "").strip().lower()
	if not slug:
		frappe.throw(_("subdomain is required"))
	if frappe.db.exists("CMS Project", {"project_slug": slug}):
		frappe.throw(_("Website address {0} is taken").format(slug))
	owner = _ensure_user(owner_email, owner_name)
	doc = frappe.get_doc({"doctype": "CMS Project", "project_name": _unique_name((project_name or slug).strip()), "project_slug": slug,
		"status": "Draft", "frontend_stack": "react" if frontend_stack == "react" else "vue"})
	if owner:
		doc.append("members", {"user": owner, "access": "Owner"})
	doc.flags.ignore_permissions = True
	doc.insert()
	plan.remember_project(doc.name, entitlements)
	frappe.db.commit()
	return {"project": doc.name, "slug": slug, "site_url": frappe.utils.get_url(), "app_version": _version()}


@frappe.whitelist(allow_guest=True)
def bootstrap(owner_email=None, owner_name=None, entitlements=None, password_hash=None, setup=None):
	"""First call on a site of its own: make the owner and take the entitlements."""
	authorize()
	owner = _ensure_user(owner_email, owner_name, password_hash)
	if owner:
		roles = set(frappe.get_roles(owner))
		user = frappe.get_doc("User", owner)
		for role in ("System Manager", "CMS Manager"):
			if frappe.db.exists("Role", role) and role not in roles:
				user.append("roles", {"role": role})
		user.flags.ignore_permissions = True
		user.save()
	if isinstance(entitlements, str):
		entitlements = json.loads(entitlements or "{}")
	if entitlements and entitlements.get("project"):
		plan.remember_project(entitlements["project"], entitlements)
	frappe.db.commit()
	return {"owner": owner, "app_version": _version()}


@frappe.whitelist(allow_guest=True)
def adopt_owner_password(owner_email, password_hash):
	"""Give the owner the panel's password when this site has none for them yet."""
	authorize()
	if not frappe.db.exists("User", owner_email):
		return {"set": 0, "reason": "no such user"}
	if frappe.db.sql("select 1 from `__Auth` where doctype='User' and name=%s and fieldname='password'", owner_email):
		return {"set": 0, "reason": "already has a password"}
	_set_password_hash(owner_email, password_hash)
	return {"set": 1}


@frappe.whitelist(allow_guest=True)
def set_project_status(project, status):
	authorize()
	doc = _project(project)
	doc.status = STATUS_MAP.get(str(status).lower(), doc.status)
	doc.flags.ignore_permissions = True
	doc.save()
	frappe.cache().delete_key(f"go1saas:preview:{project}")
	return {"project": project, "status": doc.status}


@frappe.whitelist(allow_guest=True)
def set_frontend_stack(project, stack):
	authorize()
	if stack not in ("vue", "react"):
		frappe.throw(_("Unknown stack {0}").format(stack))
	frappe.db.set_value("CMS Project", _project(project).name, "frontend_stack", stack)
	return {"project": project, "stack": stack}


def _domains():
	raw = frappe.db.get_global(DOMAINS_KEY)
	try:
		return json.loads(raw) if raw else {}
	except ValueError:
		return {}


@frappe.whitelist(allow_guest=True)
def set_domain(project, domain, action="add"):
	"""Map (or unmap) a hostname to a website; `route_custom_domain` reads the map."""
	authorize()
	_project(project)
	domain = (domain or "").strip().lower()
	data = _domains()
	if action in ("remove", "delete", "detach"):
		data.pop(domain, None)
	else:
		data[domain] = project
	frappe.db.set_global(DOMAINS_KEY, json.dumps(data))
	return {"domain": domain, "project": project, "action": action}


def _slug_of(project):
	return frappe.db.get_value("CMS Project", project, "project_slug") or project


def resolve_hostname(host):
	"""{"project", "slug"} for a hostname this site serves as one website, or None.
	The panel's own site also answers for platform subdomains and verified custom domains (go1saas.hosting); every
	other site knows only what the panel told it through set_domain."""
	host = (host or "").split(":")[0].strip().lower().rstrip(".")
	if not host:
		return None
	project = _domains().get(host)
	if project and frappe.db.exists("CMS Project", project):
		return {"project": project, "slug": _slug_of(project)}
	if "go1saas" in frappe.get_installed_apps():
		from go1saas import hosting

		found = hosting.resolve_project_from_hostname(host)
		if found and found.get("status") in (None, "active"):   # a suspended or over-quota website is not served
			return {"project": found["project"], "slug": found["slug"]}
	return None


def _scoped(path, slug):
	"""The address a website's visitor asked for, as the page route that serves it: / -> /<slug>/home, /about -> /<slug>/about."""
	path = "/" + (path or "/").lstrip("/")
	if path.rstrip("/") == "":
		return f"/{slug}/home"
	if path == f"/{slug}" or path.startswith(f"/{slug}/"):
		return path
	return f"/{slug}{path}"


def host_scope():
	"""cms_host_provider: {"project", "slug", "host", "main"} when this request is on one website's own address, else None."""
	request = getattr(frappe.local, "request", None)
	if not request:
		return None
	host = (request.host or "").split(":")[0].lower()
	cache = getattr(frappe.local, "cms_host_scope_cache", None)
	if cache and cache[0] == host:
		return cache[1]
	found = resolve_hostname(host)
	scope = {"project": found["project"], "slug": found["slug"], "host": host, "main": False} if found else None
	frappe.local.cms_host_scope_cache = (host, scope)
	return scope


def public_route(route, scope=None):
	"""A page route as the visitor sees it on a website's own address: <slug>/products -> products, <slug>/home -> the root."""
	route = (route or "").strip("/")
	scope = scope or host_scope()
	if not scope:
		return route
	slug = scope["slug"]
	if route == slug or route == f"{slug}/home":
		return ""
	if route.startswith(slug + "/"):
		return route[len(slug) + 1:]
	return route


def route_custom_domain(host=None):
	"""cms_host_provider hook (cms_frontend.extensions.before_request): on a website's own address
	(<slug>.<platform domain> or its custom domain) scope the request to that website. The page's route gets the
	website's slug in front, so every website's pages stay apart; the admin, the desk, the API and assets are left alone."""
	request = getattr(frappe.local, "request", None)
	if not request:
		return None
	found = resolve_hostname(host or request.host)
	if not found:
		return None
	slug = found["slug"]
	frappe.local.cms_scoped_project = found["project"]
	frappe.local.cpanel_scope = {"project": found["project"], "main": False}
	path = request.path or "/"
	if path.startswith("/api/method/go1_cms.go1_cms.api.get_page_content"):
		route = (frappe.local.form_dict.get("route") or "").strip()
		if route in ("", "/") or not (route.strip("/") == slug or route.strip("/").startswith(slug + "/")):
			frappe.local.form_dict["route"] = _scoped(route, slug).lstrip("/")
		return found
	from cms_frontend.not_found import is_reserved

	if not is_reserved(path):
		request.path = _scoped(path, slug)
	return found


@frappe.whitelist(allow_guest=True)
def set_default_project(project):
	"""The website the main domain serves."""
	authorize()
	_project(project)
	frappe.db.set_global(DEFAULT_KEY, project)
	return {"project": project}


def _pages(project, fields):
	return frappe.get_all("Web Page Builder", filters={"project": project}, fields=fields, order_by="modified desc")


@frappe.whitelist(allow_guest=True)
def project_preview(project, limit=3):
	"""Page counts and the sections of the first pages, for the panel's website cards."""
	authorize()
	_project(project)
	rows = _pages(project, ["name", "route", "published", "layout_json", "draft_layout_json", "modified"])
	pages = []
	for r in rows[: int(limit or 3)]:
		try:
			layout = json.loads(r.layout_json or r.draft_layout_json or "[]")
		except ValueError:
			layout = []
		sections = layout.get("sections") if isinstance(layout, dict) else layout
		pages.append({"route": r.route, "published": r.published, "modified": str(r.modified), "sections": sections or []})
	live = sum(1 for r in rows if r.published)
	return {"project": project, "page_count": len(rows), "live_count": live, "content_count": len(rows), "pages": pages}


@frappe.whitelist(allow_guest=True)
def site_projects():
	"""Every website on this site with its page counts (the panel's Websites list)."""
	authorize()
	out = []
	for p in frappe.get_all("CMS Project", fields=["name", "project_name", "project_slug", "status", "modified"], order_by="modified desc"):
		rows = _pages(p.name, ["published"])
		live = sum(1 for r in rows if r.published)
		out.append({**p, "last_modified": str(p.modified), "page_count": len(rows), "live_count": live, "draft_count": len(rows) - live,
			"previews": []})
	return out


@frappe.whitelist(allow_guest=True)
def clear_cache():
	authorize()
	frappe.clear_cache()
	return {"ok": 1}


# ── login links ──────────────────────────────────────────────────────────────

def verify_token(token):
	"""The payload of a panel login token ({"u", "p", "e", "n"}), or None."""
	from go1saas import sso

	return sso.verify(frappe.conf.get("go1saas_secret") or "", token or "")


@frappe.whitelist(allow_guest=True)
def sso(token=None):
	"""A login link minted by the panel (go1saas.sso.mint): sign the user in and land in the builder."""
	payload = verify_token(token)
	if not payload or not payload.get("u") or not frappe.db.exists("User", payload["u"]):
		frappe.throw(_("This sign-in link is invalid or has expired."), frappe.AuthenticationError)
	nonce = f"go1_cms:sso:{payload.get('n')}"
	if frappe.cache().get_value(nonce):
		frappe.throw(_("This sign-in link was already used."), frappe.AuthenticationError)
	frappe.cache().set_value(nonce, 1, expires_in_sec=300)
	from frappe.auth import LoginManager

	frappe.local.login_manager = LoginManager()
	frappe.local.login_manager.login_as(payload["u"])
	frappe.local.response["type"] = "redirect"
	frappe.local.response["location"] = "/cms/pages" + (f"?project={frappe.utils.quote(payload['p'])}" if payload.get("p") else "")
