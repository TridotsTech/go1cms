import frappe
from pypika import Criterion


@frappe.whitelist()
def get_views(doctype):
    if frappe.session.user == "Guest":
        frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

    check_doc = frappe.db.exists(
        {"doctype": "MBW Client Website", "edit": 1})

    views = {
        'website_primary': 1 if check_doc else 0,
        'type_category': 'Website công ty'
    }
    return views
