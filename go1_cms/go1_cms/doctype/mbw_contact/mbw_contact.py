# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MBWContact(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Họ và tên",
                "type": "Data",
                "key": "full_name",
                "width": "10rem"
            },
            {
                "label": "Email",
                "type": "Data",
                "key": "email",
                "width": "16rem"
            },
            {
                "label": "Số điện thoại",
                "type": "Data",
                "key": "phone_number",
                "width": "10rem"
            },
            {
                "label": "UTM Source",
                "type": "Data",
                "key": "utm_source",
                "width": "10rem"
            },
            {
                "label": "UTM Campaign",
                "type": "Data",
                "key": "utm_campaign",
                "width": "10rem"
            },
            {
                "label": "Thời gian gửi",
                "type": "Datetime",
                "key": "send_time",
                "width": "12rem"
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
            "full_name",
            "email",
            "phone_number",
            "utm_source",
            "utm_campaign"
        ]
        return {'columns': columns, 'rows': rows}
