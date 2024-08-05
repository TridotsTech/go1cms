# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class SectionTemplate(Document):
    def validate(self):
        if self.content:
            for item in self.content:
                if item.field_label and not item.field_key:
                    item.field_key = item.field_label.lower().replace(' ', '_')
                    check_existing = list(filter(lambda x: (
                        x.field_key == item.field_key and x.name != item.name), self.content))
                    if check_existing:
                        item.field_key = item.field_key + \
                            '{0}'.format(frappe.generate_hash(length=4))
                if item.field_type == "List":
                    if item.content:
                        ct_json = json.loads(item.content)
                        for index, ct_item in enumerate(ct_json):
                            ct_item['idx'] = index + 1
                        item.content = json.dumps(ct_json)

        import re
        self.route = re.sub('[^a-zA-Z0-9 \n\.]', '-', self.name.lower())


@frappe.whitelist()
def get_linked_documents(dt, image_option):
    document_fields = frappe.get_meta(dt, cached=True)
    filtered_list = []
    if image_option == 'Child Table':
        filtered_list = list(
            filter(lambda x: x.fieldtype == 'Table', document_fields.fields))
    else:
        filtered_list = list(
            filter(lambda x: x.fieldtype == 'Link', document_fields.fields))
    if filtered_list:
        docs_list = []
        for item in filtered_list:
            docs_meta = frappe.get_meta(item.options, cached=True)
            attach_fields = list(filter(lambda x: x.fieldtype in [
                                 'Attach Image', 'Attach'], docs_meta.fields))
            if attach_fields:
                docs_list.append(
                    {'document': item.options, 'fields': attach_fields})
        return docs_list


@frappe.whitelist()
def get_css_fields():
    # result = frappe.get_list("CSS Fields",fields=['*'])
    # return result
    result = frappe.db.get_single_value('CMS Settings', 'styles_to_update')
    return json.loads(result)
