# Copyright (c) 2026, Go1 CMS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class WebPagePublishLog(Document):
	"""One row per successful publish of a Web Page Builder page.

	Written only by the publish APIs, never by hand — the whole point is that every
	entry corresponds to an actual publish that happened.
	"""

	pass


def record_publish(page_doc, source="Page"):
	"""Record that `page_doc` was just published. Never raises: a logging failure
	must not roll back or mask a publish that already succeeded."""
	try:
		frappe.get_doc({
			"doctype": "Web Page Publish Log",
			"page": page_doc.name,
			"page_title": getattr(page_doc, "page_title", None) or page_doc.name,
			"project": getattr(page_doc, "project", None),
			"published_on": now(),
			"published_by": frappe.session.user,
			"source": source,
		}).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Web Page Publish Log Error")
