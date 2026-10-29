# Copyright (c) 2026, Tridotstech and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class WebsiteTemplatePurchase(Document):
	"""A store template this site bought (Paid) or took (Free). Written by cms_frontend.template_store
	only; a Paid row's Razorpay payment id proves the purchase to the store (it keeps no records)."""
