# Copyright (c) 2026, Go1 CMS and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class DocTag(Document):
	# Named after the tag itself (autoname field:tag); the docs API lower-cases
	# tags before it creates them, so "SEO" and "seo" are one tag.
	pass
