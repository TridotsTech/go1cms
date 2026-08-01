# Copyright (c) 2026, Go1 CMS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import random_string


class WebPageShare(Document):
	"""A view-only external preview link for one Web Page Builder page."""

	def before_insert(self):
		if not self.token:
			self.token = random_string(32)

	def validate(self):
		if not self.invites:
			self.invites = "[]"
