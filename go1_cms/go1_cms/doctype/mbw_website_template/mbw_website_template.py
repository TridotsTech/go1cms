# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
import time


class MBWWebsiteTemplate(Document):
    def before_naming(self):
        if not self.custom_name:
            self.custom_name = "WT-{}".format(getStrTimestamp())

    def validate(self):
        if self.template_in_use == 1:
            existing_list = frappe.db.sql(
                '''UPDATE `tabMBW Website Template` SET template_in_use=0 WHERE name!="{web_name}" AND template_in_use=1'''.format(web_name=self.name))
            frappe.db.commit()

    @staticmethod
    def default_list_data():
        columns = []

        rows = [
            "name",
            "creation",
            "modified_by",
            "modified",
            "owner",
            "image_preview",
            "template_name",
            "template_in_use",
            "installed_template"
        ]
        return {'columns': columns, 'rows': rows}


def getStrTimestamp():
    arr_time = str(time.time()).split('.')
    while (len(arr_time[1]) < 7):
        arr_time[1] += '0'

    return arr_time[0] + arr_time[1]
