# -*- coding: utf-8 -*-
# Copyright (c) 2022, Tridots Tech and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
import json
import os
import urllib.parse
from frappe.utils import encode, get_files_path, getdate
from frappe.model.mapper import get_mapped_doc
from frappe.website.website_generator import WebsiteGenerator
# from ecommerce_business_store.ecommerce_business_store.api import check_domain, get_business_from_login
from frappe.model.naming import make_autoname
# from ecommerce_business_store.utils.setup import get_settings_from_domain, \
# 	get_settings_value_from_domain, get_theme_settings
# from ecommerce_business_store.cms.api import get_template_folder, unescape
from urllib.parse import urljoin, unquote, urlencode
from frappe.model.document import Document


class FooterComponent(Document):
    def on_update(self):
        self.construct_html('web', 'web_section')

    def construct_html(self, view_type, ref_field):
        result = self.get_json_data(ref_field)
        path = get_files_path()
        if not os.path.exists(os.path.join(path, 'data_source')):
            frappe.create_folder(os.path.join(path, 'data_source'))

        with open(os.path.join(path, 'data_source', (self.name.lower().replace(' ', '_') + '_' + view_type + '.json')), "w") as f:
            if view_type == "mobile":
                content = json.dumps(json.loads(
                    frappe.as_json(result)), separators=(',', ':'))
                # f.write(frappe.as_json(result))
                f.write(content)
            else:
                # f.write(frappe.as_json(result))
                content = json.dumps(json.loads(
                    frappe.as_json(result)), separators=(',', ':'))
                # f.write(frappe.as_json(result))
                # frappe.log_error(content,'content')
                f.write(content)

    def get_json_data(self, ref_field):
        results = []
        for item in self.as_dict()[ref_field]:
            doc = frappe.get_doc('Page Section', item.section)
            obj = doc.run_method('section_data')
            obj["column_index"] = item.get("column_index")
            results.append(obj)
        return results


@frappe.whitelist()
def get_footer_layouts():
    try:
        final_data = []
        all__data = frappe.db.get_list("Footer Layout", fields=[
                                       "name", "title", "preview", "layout_json"], filters={"is_active": 1})
        for k in all__data:
            final_data.append({"layout_json": json.loads(
                k.layout_json), "preview": k.preview, "title": k.title, "name": k.name})
        return final_data
    except Exception:
        frappe.log_error(frappe.get_traceback(
        ), "go1_cms.go1_cms.doctype.footer_component.footer_component.get_footer_layouts")
