# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWBlogTag(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Tên tag",
                "type": "Data",
                "key": "title",
                "width": "473px"
            },
            {
                "label": "Hành động",
                "key": "action_button"
            }
        ]
        rows = [
            "name",
            "creation",
            "modified_by",
            "modified",
            "action_button",
            "title"
        ]
        return {'columns': columns, 'rows': rows}
