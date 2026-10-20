"""First content for the docs: two spaces, the feature catalogue, the articles.

    bench --site <site> execute go1_cms.docs.seed.run
    bench --site <site> execute go1_cms.docs.seed.run --kwargs "{'reset': 1}"
    bench --site <site> execute go1_cms.docs.seed.run --kwargs "{'sync_order': 1}"

Idempotent: a space, article or feature that already exists is left exactly as
an editor left it, unless `reset=1`, which rewrites the seeded rows (and only
those) from the files here. `setup.after_migrate` runs it once on a site that
has no Doc Space yet, so deploying is `git pull && bench migrate`.

The GO1 CMS space is the 22 articles the product website already published
under /docs (content/cms/*.md, same slugs, same order), so every link to
/docs/<slug> keeps working. The GO1 Panel space follows the docs plan: one
short article per panel feature, kept Draft (and the space unpublished) until
the panel is launched.
"""

import os
import re

import frappe

CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")

SPACES = [
	{"slug": "cms", "title": "GO1 CMS", "description": "Build, bind and publish websites with the visual builder.",
	 "icon": "layers", "sort_order": 1, "is_published": 1, "is_primary": 1},
	{"slug": "panel", "title": "GO1 Panel", "description": "Plans, sites, domains, billing and your team in the hosted control panel.",
	 "icon": "grid", "sort_order": 2, "is_published": 0, "is_primary": 0},
	{"slug": "guide", "title": "Site owner guide", "description": "Plain-language help for every screen of the admin.",
	 "icon": "book", "sort_order": 3, "is_published": 1, "is_primary": 0},
]

# (sidebar group, [(slug, title)]) in reading order: the product website's own order.
CMS_ARTICLES = [
	("Get started", [("introduction", "Introduction"), ("get-started", "Get started"), ("create-a-website", "Create a website"),
	                 ("builder-basics", "Builder basics"), ("publish", "Publish your site")]),
	("Build", [("elements", "Elements"), ("canvas-and-selection", "Canvas, selection and layers"), ("inspector", "The inspector"),
	           ("text-editing", "Editing text"), ("layout-and-responsive", "Layout and responsive"),
	           ("styles-and-states", "Styles, states and animations"), ("style-presets", "Style presets and site CSS"),
	           ("sections-and-templates", "Sections and templates"), ("components", "Components and reusable blocks"),
	           ("theme-studio", "Theme Studio"), ("menus-and-navigation", "Menus and navigation"),
	           ("header-and-footer", "Header, footer and responsive header"), ("sliders-tabs-accordions", "Sliders, tabs and accordions"),
	           ("icons-shapes-media", "Icons, shapes and media"), ("custom-code", "Custom CSS, Global JS and embeds"),
	           ("keyboard-shortcuts", "Keyboard shortcuts")]),
	("Content and data", [("collections", "Collections"), ("data-binding", "Data binding and repeaters"),
	                      ("variables-and-events", "Variables, resources and events"), ("filters-and-lists", "Filters, search and dynamic lists"),
	                      ("query-builder", "Query builder"), ("forms", "Forms"), ("form-builder", "Form builder"),
	                      ("form-inbox-and-emails", "Form inbox and emails"), ("blog", "Blog and posts"),
	                      ("media-library", "Media library"), ("comments-and-reviews", "Comments and client review")]),
	("AI", [("ai-builder", "AI builder"), ("ai-editor", "AI editor in the builder"),
	        ("ai-copy-and-images", "AI copywriting, section redo and images"), ("ai-settings-and-limits", "AI providers, keys and limits")]),
	("Portals", [("portals", "Portals and members"), ("portal-data-sources", "Portal data sources"),
	             ("bookings-and-memberships", "Bookings, memberships and payments"), ("sign-in-providers", "Sign-in providers")]),
	("Grow", [("plans-and-limits", "Plans and limits"), ("domains", "Domains"), ("team", "Team and sharing"),
	          ("page-management", "Managing pages"), ("seo-and-analytics", "SEO and analytics"), ("seo-in-depth", "SEO in depth"),
	          ("analytics-in-depth", "Analytics in depth"), ("performance", "Speed and caching"), ("plugins", "Plugins and e-commerce")]),
	("Integrations", [("erpnext-storefront", "ERPNext storefront"), ("razorpay", "Razorpay payments"),
	                  ("google-analytics", "Google Analytics 4 and cookie consent"), ("chat-whatsapp-popups", "Live chat, WhatsApp and popups"),
	                  ("stock-photos-and-image-generation", "Stock photos and AI images"),
	                  ("figma-and-imports", "Figma, Frappe Builder and the clipper")]),
	("Developers", [("architecture", "How GO1 CMS is built"), ("extending", "Extending GO1 CMS"),
	                ("server-rendering", "Server rendering and the React runtime"), ("api-reference", "API reference"),
	                ("self-hosting", "Self-hosting (open source)"), ("mcp-server", "MCP server and API"), ("faq", "FAQ")]),
]

# OPS-08: the site owner's manual, one article per admin screen (content/guide/*.md), in reading order.
GUIDE_ARTICLES = [
	("Get around", [("how-the-admin-is-laid-out", "How the admin is laid out"), ("glossary", "Glossary"), ("home", "Home")]),
	("Build", [("projects", "Projects and pages"), ("builder", "The page builder"), ("library", "Library"),
	           ("theme", "Theme"), ("menus", "Menus")]),
	("Content", [("posts", "Posts"), ("comments", "Comments"), ("collections", "Collections and content types"),
	             ("forms", "Forms"), ("media", "Media")]),
	("Apps", [("plugins", "Plugins"), ("portal", "Portal")]),
	("Go live", [("publish", "Publish"), ("seo", "SEO"), ("popups", "Popups"), ("analytics", "Analytics")]),
	("Account", [("docs-admin", "Docs"), ("ai-settings", "AI Settings"), ("control-panel", "The control panel")]),
]

# Related features shown under an article, beyond the feature's own "Learn more" article.
ARTICLE_FEATURES = {
	"canvas-and-selection": ["visual-page-builder"], "inspector": ["visual-page-builder", "responsive-and-state-styles"],
	"components": ["section-and-website-templates"], "variables-and-events": ["data-collections-and-repeaters"],
	"filters-and-lists": ["data-collections-and-repeaters"], "query-builder": ["data-collections-and-repeaters"],
	"form-builder": ["forms-and-web-forms"], "form-inbox-and-emails": ["forms-and-web-forms"],
	"ai-editor": ["ai-site-builder"], "ai-copy-and-images": ["ai-site-builder"], "seo-in-depth": ["seo-and-sitemap"],
	"analytics-in-depth": ["analytics"], "google-analytics": ["analytics", "plugins"], "erpnext-storefront": ["plugins"],
	"chat-whatsapp-popups": ["plugins"], "page-management": ["publishing-and-share-links"],
	"comments-and-reviews": ["publishing-and-share-links"], "api-reference": ["mcp-server"], "extending": ["plugins"],
}

# slug, title, category, (starter, medium, premium) as True/False or a note, tagline, article slug, highlight
BUILDER_FEATURES = [
	("visual-page-builder", "Visual page builder", "Builder", (True, True, True),
	 "A Framer-style canvas with an inspector, layers and in-place text editing.", "builder-basics", True),
	("section-and-website-templates", "Section and website templates", "Builder", (True, True, True),
	 "283 core sections and whole-site templates for 18 industries, all editable.", "sections-and-templates", True),
	("responsive-and-state-styles", "Responsive and state styles", "Builder", (True, True, True),
	 "Desktop, tablet and mobile styles, plus hover, active and focus.", "layout-and-responsive", False),
	("animations", "Animations", "Builder", (True, True, True),
	 "Entrance and loop animations from one catalogue, by element, section or page.", "styles-and-states", False),
	("data-collections-and-repeaters", "Data collections and repeaters", "Builder", (True, True, True),
	 "Bind lists to doctypes, saved queries or APIs, with paging and filters.", "data-binding", True),
	("forms-and-web-forms", "Forms and web forms", "Builder", (True, True, True),
	 "Forms that save to any doctype, with an inbox, emails and a captcha.", "forms", False),
	("theme-studio-and-brand-kit", "Theme Studio and brand kit", "Builder", (True, True, True),
	 "Per-project colour, type and spacing tokens that every page follows.", "theme-studio", True),
	("ai-site-builder", "AI site builder", "Builder", (False, True, True),
	 "Describe a site and get editable pages, section by section.", "ai-builder", True),
	("seo-and-sitemap", "SEO and sitemap", "Builder", (True, True, True),
	 "Per-page meta, a server-rendered head and an XML sitemap.", "seo-and-analytics", False),
	("analytics", "Analytics", "Builder", (True, True, True),
	 "First-party page views and trends, with GA4 when you connect it.", "seo-and-analytics", False),
	("plugins", "Plugins", "Integrations", (True, True, True),
	 "Turn on e-commerce, chat, consent, popups and more per project.", "plugins", False),
	("mcp-server", "MCP server", "Integrations", (False, False, True),
	 "Drive the builder from Claude or any MCP client.", "mcp-server", False),
	("publishing-and-share-links", "Publishing and share links", "Builder", (True, True, True),
	 "Draft, publish and roll back; share view-only previews.", "publish", True),
]

# Plan columns follow the control-panel decisions of 2026-09-28: Starter is one
# website on a shared site, Medium up to five websites, Premium a dedicated server.
PANEL_FEATURES = [
	("sign-up-and-workspace", "Sign up and workspace", "Panel", (True, True, True),
	 "Create an account and a workspace for your team.", "create-your-account", "Create your account"),
	("subscription-plans", "Subscription plans", "Billing", (True, True, True),
	 "Start free on Starter, move to Medium or Premium when you grow.", "choose-a-plan", "Choose a plan"),
	("one-click-site-provisioning", "One-click site provisioning", "Hosting", (True, True, True),
	 "A new website is ready in minutes, no server work.", "your-first-site", "Your first site"),
	("single-sign-on-to-the-builder", "Single sign-on to the builder", "Panel", (True, True, True),
	 "Open any website's builder from the panel without a second sign-in.", "open-the-builder", "Open the builder from the panel"),
	("razorpay-billing-and-invoices", "Razorpay billing and invoices", "Billing", (False, True, True),
	 "Pay by card or UPI and download every invoice.", "pay-and-download-invoices", "Pay and download invoices"),
	("site-and-bandwidth-limits", "Site and bandwidth limits", "Hosting", ("1 website", "5 websites", "Unlimited"),
	 "Clear limits per plan, with storage packs when you need more.", "understand-your-limits", "Understand your limits"),
	("custom-domains-with-tls", "Custom domains with TLS", "Hosting", (False, True, True),
	 "Use your own domain with automatic HTTPS.", "connect-a-domain", "Connect a domain"),
	("team-members-and-roles", "Team members and roles", "Team", (False, True, True),
	 "Invite people and choose what each of them may do.", "invite-your-team", "Invite your team"),
	("dedicated-server", "Dedicated server", "Hosting", (False, False, True),
	 "Premium runs on a server of its own.", "premium-hosting", "Premium hosting"),
	("usage-dashboard", "Usage dashboard", "Panel", (True, True, True),
	 "See views, bandwidth and storage against your plan.", "read-your-usage", "Read your usage"),
]

_H1 = re.compile(r"^#\s+.*\n+")
_DOCS_LINK = re.compile(r"\]\(/docs/([a-z0-9-]+)(#[^)]*)?\)")


def _read_cms_article(slug, space_dir="cms"):
	"""Body Markdown and summary of one article file (content/<space_dir>/<slug>.md): the H1 is
	dropped (the title is its own field) and the lead paragraph becomes the summary."""
	with open(os.path.join(CONTENT, space_dir, slug + ".md"), encoding="utf-8") as fh:
		md = fh.read()
	md = _H1.sub("", md.lstrip(), count=1)
	paras = md.split("\n\n", 1)
	summary = paras[0].strip() if paras and not paras[0].lstrip().startswith(("#", "-", "|", "`", ">")) else ""
	body = paras[1].lstrip() if summary and len(paras) > 1 else md
	# The summary is plain text (meta description, search snippet, the lead line).
	summary = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", summary)
	summary = re.sub(r"(\*\*|__|\*|`)", "", summary)
	# Links to another docs article become relative, so they follow the space.
	body = _DOCS_LINK.sub(lambda m: "](../%s%s)" % (m.group(1), m.group(2) or ""), body)
	return body.strip() + "\n", summary


def _panel_body(title, tagline):
	return (
		"%s\n\n## What it does\n\n%s This article is a placeholder: it is published when the control panel is.\n\n"
		"## How to\n\n1. Sign in to the control panel.\n2. Open the screen for %s.\n3. Follow the steps shown there.\n\n"
		"> [!NOTE]\n> Screenshots for this step are added once the screen is final.\n"
	) % (tagline, tagline, title.lower())


def sync_cms_order():
	"""Put the GO1 CMS articles back in the shipped sidebar order and groups.
	Only on request: editors reorder the sidebar, and a later seed must not undo that."""
	order = 0
	for group, items in CMS_ARTICLES:
		for slug, _title in items:
			order += 10
			name = frappe.db.get_value("Doc Article", {"space": "cms", "slug": slug}, "name")
			if name:
				frappe.db.set_value("Doc Article", name, {"group_label": group, "sort_order": order, "parent_article": None})


def _upsert(doctype, filters, values, reset):
	name = frappe.db.get_value(doctype, filters, "name")
	if name and not reset:
		return name, False
	doc = frappe.get_doc(doctype, name) if name else frappe.new_doc(doctype)
	doc.update(values)
	doc.flags.ignore_permissions = True
	doc.save() if name else doc.insert()
	return doc.name, True


def run(reset=0, sync_order=0):
	from go1_cms.docs.setup import ensure_role

	ensure_role()
	reset = int(reset or 0)
	made = {"spaces": 0, "articles": 0, "features": 0}

	for s in SPACES:
		_, changed = _upsert("Doc Space", {"slug": s["slug"]}, dict(s), reset)
		made["spaces"] += changed

	# Articles first (features link to them), then the features, then the article → feature links.
	cms_names = {}
	order = 0
	for group, items in CMS_ARTICLES:
		for slug, title in items:
			order += 10
			body, summary = _read_cms_article(slug)
			name, changed = _upsert("Doc Article", {"space": "cms", "slug": slug}, {
				"title": title, "slug": slug, "space": "cms", "group_label": group, "sort_order": order,
				"summary": summary, "body_md": body, "status": "Published",
			}, reset)
			cms_names[slug] = name
			made["articles"] += changed

	guide_names = {}
	order = 0
	for group, items in GUIDE_ARTICLES:
		for slug, title in items:
			order += 10
			body, summary = _read_cms_article(slug, "guide")
			name, changed = _upsert("Doc Article", {"space": "guide", "slug": slug}, {
				"title": title, "slug": slug, "space": "guide", "group_label": group, "sort_order": order,
				"summary": summary, "body_md": body, "status": "Published",
			}, reset)
			guide_names[slug] = name
			made["articles"] += changed

	panel_names = {}
	for i, (slug, title, category, plans, tagline, art_slug, art_title) in enumerate(PANEL_FEATURES):
		name, changed = _upsert("Doc Article", {"space": "panel", "slug": art_slug}, {
			"title": art_title, "slug": art_slug, "space": "panel", "group_label": category,
			"sort_order": (i + 1) * 10, "summary": tagline, "body_md": _panel_body(title, tagline), "status": "Draft",
		}, reset)
		panel_names[slug] = name
		made["articles"] += changed

	def plan_values(plans):
		out = {}
		for key, val in zip(("starter", "medium", "premium"), plans):
			out[key] = 1 if val else 0
			out[key + "_note"] = val if isinstance(val, str) else None
		return out

	feature_rows = []
	for i, (slug, title, category, plans, tagline, art, highlight) in enumerate(BUILDER_FEATURES):
		feature_rows.append((slug, dict(title=title, slug=slug, category=category, status="Live", tagline=tagline,
		                                sort_order=(i + 1) * 10, is_highlight=1 if highlight else 0,
		                                doc_article=cms_names.get(art), **plan_values(plans)), cms_names.get(art)))
	for i, (slug, title, category, plans, tagline, art_slug, _t) in enumerate(PANEL_FEATURES):
		feature_rows.append((slug, dict(title=title, slug=slug, category=category, status="Planned", tagline=tagline,
		                                sort_order=(i + 1) * 10, is_highlight=0,
		                                doc_article=panel_names.get(slug), **plan_values(plans)), panel_names.get(slug)))
	for slug, values, article in feature_rows:
		_, changed = _upsert("Product Feature", {"slug": slug}, values, reset)
		made["features"] += changed
		if article and changed:
			doc = frappe.get_doc("Doc Article", article)
			if slug not in [f.feature for f in doc.features]:
				doc.append("features", {"feature": slug})
				doc.flags.ignore_permissions = True
				doc.save()

	for slug, features in ARTICLE_FEATURES.items():
		name = cms_names.get(slug)
		if not name:
			continue
		doc = frappe.get_doc("Doc Article", name)
		have = [f.feature for f in doc.features]
		missing = [f for f in features if f not in have and frappe.db.exists("Product Feature", f)]
		if missing and (reset or not have):
			for f in missing:
				doc.append("features", {"feature": f})
			doc.flags.ignore_permissions = True
			doc.save()

	if sync_order:
		sync_cms_order()

	if reset or not frappe.db.get_value("Doc Space", "cms", "default_article"):
		frappe.db.set_value("Doc Space", "cms", "default_article", cms_names.get("introduction"))
	if reset or not frappe.db.get_value("Doc Space", "panel", "default_article"):
		frappe.db.set_value("Doc Space", "panel", "default_article", panel_names.get("sign-up-and-workspace"))

	if reset or not frappe.db.get_value("Doc Space", "guide", "default_article"):
		frappe.db.set_value("Doc Space", "guide", "default_article", guide_names.get(GUIDE_ARTICLES[0][1][0][0]))

	from go1_cms.docs.api import clear_cache

	clear_cache()
	return made
