# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Menu(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Menu name",
                "type": "Data",
                "key": "title",
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
            "modified",
            "action_button",
            "title",
            "id_client_website"
        ]
        return {'columns': columns, 'rows': rows}

    # def validate(self):
    # 	if self.mega_menu_number_of_columns > 4:
    # 		frappe.throw('Maximun no of columns should be less than or euqal to <b>4</b>')
