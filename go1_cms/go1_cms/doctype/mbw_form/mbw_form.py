# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWForm(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Form name",
                "type": "Data",
                "key": "form_name",
                "width": "473px"
            },
            {
                "label": "Form type",
                "type": "Data",
                "key": "form_type",
                "width": "15rem"
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
            "modified",
            "action_button",
            "form_name",
            "id_client_website",
            "form_type"
        ]
        return {'columns': columns, 'rows': rows}
