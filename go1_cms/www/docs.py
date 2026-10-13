# Serves /docs and everything under it (route rules in cms_frontend/hooks.py,
# ahead of the SPA catch-all). The page is rendered here, on the server, from
# the HTML each article stored when it was saved — so a cold load is a handful
# of queries, no Markdown work and no JavaScript needed to read it.
#
# What each address shows is decided in go1_cms.docs.api.page_context.

import json

import frappe
from frappe import _

no_cache = 1
SITE_NAME = "GO1 CMS"


def _site_base():
	host = frappe.local.conf.host_name or frappe.local.conf.hostname
	if host:
		return (host if host.startswith(("http://", "https://")) else "https://" + host).rstrip("/")
	return frappe.utils.get_url().rstrip("/")


def _sign_in_route():
	"""The product website's own sign-in page when it has one, else Frappe's."""
	if frappe.db.exists("Web Page Builder", {"route": "signin", "published": 1}):
		return "/signin"
	return "/login"


GITHUB = "https://github.com/TridotsTech"


def _site_chrome():
	"""The product website's header and footer links, for the pages it actually has:
	Learn, Pricing and sign-up appear only where those pages are published, and the
	control-panel button only where the panel is installed."""
	routes = set(frappe.get_all("Web Page Builder", filters={"published": 1,
	                            "route": ["in", ["learn", "pricing", "signup", "signin"]]}, pluck="route"))
	nav = [{"label": "Docs", "href": "/docs", "key": "docs"}]
	if "learn" in routes:
		nav.append({"label": "Learn", "href": "/learn", "key": "learn"})
	if "pricing" in routes:
		nav.append({"label": "Pricing", "href": "/pricing", "key": "pricing"})
	has_panel = "go1_cpanel" in frappe.get_installed_apps()
	logo = "/assets/go1_cpanel/site/go1-cms-logo.svg" if has_panel else "/assets/cms_frontend/frontend/favicon.svg"
	return {
		"nav": nav, "github": GITHUB, "logo_url": logo,
		"signup_route": "/signup" if "signup" in routes else None,
		"panel_route": "/cms/panel" if has_panel else "/cms",
		"panel_label": "Open control panel" if has_panel else "Open the CMS",
	}


def get_context(context):
	from go1_cms.docs import api, render

	context.no_cache = 1
	path = frappe.form_dict.get("doc_path") or ""
	query = {k: frappe.form_dict.get(k) for k in ("q", "space", "roadmap")}
	data = api.page_context(path, query)
	if not data:
		raise frappe.PageDoesNotExistError
	if data.get("view") == "redirect":
		frappe.local.flags.redirect_location = data["location"]
		raise frappe.Redirect(302)

	context.update(data)
	base = _site_base()
	context.site_name = SITE_NAME
	context.site_base = base
	context.sign_in_route = _sign_in_route()
	context.update(_site_chrome())
	context.signed_in = frappe.session.user != "Guest"
	context.code_css = render.code_css()
	context.csrf_token = frappe.sessions.get_csrf_token() if context.signed_in else ""
	context.current_path = "/" + ("docs/" + path.strip("/") if path.strip("/") else "docs")

	view = data["view"]
	title, description, og_type, json_ld = "Docs", "", "website", None
	if view == "landing":
		title = "%s Docs" % SITE_NAME
		description = "Guides and reference for building, binding and publishing websites with %s." % SITE_NAME
	elif view == "article":
		art = data["article"]
		title = "%s · %s Docs" % (art["title"], data["space"].title)
		description = art["summary"]
		og_type = "article"
		json_ld = {
			"@context": "https://schema.org", "@type": "TechArticle", "headline": art["title"],
			"description": art["summary"], "url": base + art["route"],
			"dateModified": art["modified"][:19].replace(" ", "T"),
		}
		if art.get("published_on"):
			json_ld["datePublished"] = art["published_on"][:19].replace(" ", "T")
	elif view == "search":
		title = "Search%s · Docs" % ((": " + data["q"]) if data.get("q") else "")
	elif view == "features":
		title = "Features · %s" % SITE_NAME
		description = "Everything %s does, by area, with the plans that include it." % SITE_NAME
	elif view == "feature":
		f = data["feature"]
		title = "%s · %s" % (f["title"], SITE_NAME)
		description = f.get("tagline") or ""
	elif view == "pricing":
		title = "Plans compared · %s" % SITE_NAME
		description = "Which features each %s plan includes." % SITE_NAME
	elif view == "empty_space":
		title = "%s · Docs" % data["space"].title

	canonical = data.get("canonical") or (data["article"]["route"] if view == "article" else context.current_path)
	context.meta_title = title
	context.meta_description = description
	context.og_type = og_type
	context.canonical_url = base + canonical
	context.json_ld = json.dumps(json_ld).replace("</", "<\\/") if json_ld else ""
	context.robots = "noindex,nofollow" if (view == "search" or (view == "article" and data["article"]["status"] != "Published")) else "index,follow"
	# Guests get an ETag and revalidate (cms_frontend http_cache); editors see drafts, so never cache theirs.
	if not context.signed_in:
		frappe.local.cms_visitor_page = True
	return context
