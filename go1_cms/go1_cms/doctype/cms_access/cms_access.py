# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CMSAccess(Document):
    def on_update(self):
        frappe.publish_realtime('dashboard_update', message={})
