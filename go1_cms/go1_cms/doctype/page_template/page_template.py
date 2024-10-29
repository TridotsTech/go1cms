# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PageTemplate(Document):
    def after_delete(self):
        for item in self.web_section:
            frappe.delete_doc('Page Section', item.section)
