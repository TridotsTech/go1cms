import frappe
from pypika import Criterion


@frappe.whitelist()
def get_views(doctype):
    if frappe.session.user == "Guest":
        frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

    check_doc = frappe.db.get_value('MBW Client Website', {'edit': 1})
    list_page = []
    type_category = ''
    name_web = ''
    if check_doc:
        doc = frappe.get_doc('MBW Client Website', check_doc)
        list_page = doc.page_websites
        type_category = doc.type_template
        name_web = doc.name_web

    views = {
        'website_primary': 1 if check_doc else 0,
        'type_category': type_category,
        'list_page': list_page,
        'name_web': name_web
    }
    return views
