# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWWebsiteTemplate(Document):
    @staticmethod
    def default_list_data():
        columns = []

        rows = [
            "name",
            "creation",
            "modified_by",
            "modified",
            "_assign",
            "owner",
            "image_preview",
        ]
        return {'columns': columns, 'rows': rows}
