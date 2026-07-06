# Copyright (c) 2026, GO1 CMS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CMSPageBuilder(Document):
	"""
	Main CMS Page Builder document
	Manages multiple pages and their sections with full CRUD capabilities
	"""
	website = frappe._dict(
		route_field="builder_name",
		title_field="builder_title"
	)

	def validate(self):
		"""Validate builder data"""
		if not self.pages:
			frappe.throw("At least one page is required")

	def before_save(self):
		"""Auto-increment order for pages"""
		if self.pages:
			for idx, page in enumerate(self.pages, 1):
				if not page.order:
					page.order = idx

	def on_update(self):
		"""Update cache/notify frontend on changes"""
		frappe.publish_realtime(
			f"cms_page_builder_updated_{self.name}",
			{"doc": self},
			user=frappe.session.user
		)

@frappe.whitelist()
def get_pages(builder_name):
	"""Get all pages for a builder"""
	return frappe.get_doc("CMS Page Builder", builder_name).pages

@frappe.whitelist()
def reorder_pages(builder_name, page_order):
	"""Reorder pages within a builder"""
	doc = frappe.get_doc("CMS Page Builder", builder_name)

	# Create a map of page names to their new order
	order_map = {int(pid): order for order, pid in enumerate(page_order, 1)}

	# Update order in pages
	for page in doc.pages:
		if page.idx in order_map:
			page.order = order_map[page.idx]

	doc.save()
	frappe.msgprint("Pages reordered successfully")
	return doc.pages

@frappe.whitelist()
def add_page(builder_name, page_data):
	"""Add a new page to builder"""
	import json
	if isinstance(page_data, str):
		page_data = json.loads(page_data)

	doc = frappe.get_doc("CMS Page Builder", builder_name)
	doc.append("pages", page_data)
	doc.save()
	return {"success": True, "pages": doc.pages}

@frappe.whitelist()
def delete_page(builder_name, page_idx):
	"""Delete a page from builder"""
	doc = frappe.get_doc("CMS Page Builder", builder_name)

	# Remove page by index
	new_pages = [p for i, p in enumerate(doc.pages) if i != int(page_idx)]
	doc.pages = new_pages
	doc.save()
	return {"success": True, "pages": doc.pages}

@frappe.whitelist()
def get_page_sections(builder_name, page_name):
	"""Get all sections for a specific page"""
	doc = frappe.get_doc("CMS Page Builder", builder_name)

	# Find the page
	for page in doc.pages:
		if page.page_name == page_name:
			# Return sections associated with this page
			# For now, we'll fetch from a related doctype or return empty
			return {"page": page}

	frappe.throw(f"Page '{page_name}' not found")

@frappe.whitelist()
def save_builder_state(builder_name, state):
	"""Save complete builder state"""
	import json
	if isinstance(state, str):
		state = json.loads(state)

	doc = frappe.get_doc("CMS Page Builder", builder_name)

	# Update pages from state
	if "pages" in state:
		doc.pages = []
		for page_data in state["pages"]:
			doc.append("pages", page_data)

	doc.save()
	return {"success": True, "doc": doc}
