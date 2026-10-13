"""Make sure /docs is answered by the docs pages (www/docs.html, docs_feed.xml).

Frappe tries DocumentPage before TemplatePage, and Web Page Builder is a web-view
doctype: a builder page whose route is "docs" (the product website had 22 of
them) would be rendered for /docs instead of the docs site. Custom page
renderers run ahead of both, so this one claims the docs endpoints the route
rules resolved to and hands them to the template renderer.
"""

from frappe.website.page_renderers.template_page import TemplatePage

ENDPOINTS = ("docs", "docs_feed.xml")


class DocsPageRenderer:
	def __init__(self, path, http_status_code=None):
		self.path = path
		self.http_status_code = http_status_code
		self._delegate = None

	def can_render(self):
		if self.path not in ENDPOINTS:
			return False
		self._delegate = TemplatePage(self.path, self.http_status_code)
		return self._delegate.can_render()

	def render(self):
		return self._delegate.render()
