import frappe
from pypika import Criterion
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_views(doctype):
    if frappe.session.user == "Guest":
        frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

    check_doc = frappe.db.get_value('MBW Client Website', {'edit': 1})
    list_page = []
    type_category = ''
    name_web = ''
    if check_doc:
        doc = frappe.db.get_value('MBW Client Website', check_doc, [
                                  'type_template', 'name_web'], as_dict=1)
        list_page = frappe.db.get_all("MBW Client Website Item", filters={
            "parent": check_doc, "parentfield": "page_websites", 'allow_edit': 1}, fields=['*'], order_by="idx"
        )
        type_category = doc.type_template
        name_web = doc.name_web

    View = frappe.qb.DocType("CMS View Settings")
    query = (
        frappe.qb.from_(View)
        .select("*")
        .where(Criterion.any([View.user == '', View.user == frappe.session.user]))
    )
    if doctype:
        query = query.where(View.dt == doctype)
    views = query.run(as_dict=True)

    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    config_domain = {
        'use_other_domain': frappe.db.get_single_value(
            'CMS Settings', 'use_other_domain'),
        'domain': frappe.db.get_single_value(
            'CMS Settings', 'domain')
    }

    result = {
        'website_primary': 1 if check_doc else 0,
        'type_category': type_category,
        'list_page': list_page,
        'name_web': name_web,
        'views': views,
        'developer_mode': developer_mode,
        'config_domain': config_domain
    }
    return result
