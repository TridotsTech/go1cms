# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe import _


class MbwBlogCategory(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Category name",
                "type": "Data",
                "key": "category_title",
                "width": "473px"
            },
            {
                "label": "Last Modified",
                "type": "Datetime",
                "key": "modified"
            },
            {
                "label": "Action",
                "key": "action_button"
            }
        ]
        rows = [
            "name",
            "creation",
            "modified_by",
            "_assign", "owner",
            "modified",
            "action_button",
            "category_title"
        ]
        return {'columns': columns, 'rows': rows}
