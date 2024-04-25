import frappe
from frappe import _
from pypika import Criterion


@frappe.whitelist()
def get_client_websites():
    ClientWebsite = frappe.qb.DocType("MBW Client Website")
    query = (
        frappe.qb.from_(ClientWebsite)
        .select("*")
    )

    webs = query.run(as_dict=True)
    return webs
