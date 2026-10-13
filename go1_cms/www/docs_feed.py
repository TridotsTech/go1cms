# Serves /docs/feed.xml: the most recently published docs articles as RSS 2.0,
# for the "What's new" link and feed readers. Route rule in cms_frontend/hooks.py.

from email.utils import format_datetime

import frappe
from frappe.utils import get_datetime

no_cache = 1
base_template_path = "www/docs_feed.xml"


def get_context(context):
	from go1_cms.docs import api
	from go1_cms.www.docs import SITE_NAME, _site_base

	base = _site_base()
	items = []
	for r in api.feed_items():
		when = get_datetime(r.published_on or r.modified)
		items.append({"title": r.title, "link": base + r.route, "description": r.summary or "",
		              "pub_date": format_datetime(when.astimezone() if when.tzinfo else when.replace(tzinfo=None).astimezone())})
	context.update({"title": "%s Docs" % SITE_NAME, "link": base + "/docs", "items": items,
	                "description": "New and updated %s documentation." % SITE_NAME})
	frappe.local.response["content_type"] = "application/rss+xml"
	return context
