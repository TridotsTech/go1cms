# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class DemoBlog(WebsiteGenerator):
    def get_context(self, context):
        doc_wpb = frappe.get_doc(
            'Web Page Builder', 'Trang chi tiết tin tức eec64f5894')
        context.blog_name = self.name

        doc_wpb.get_context(context)
