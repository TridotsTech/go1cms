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


@frappe.whitelist()
def change_name_web_client_website(name, name_web):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("My website not found"), frappe.DoesNotExistError)
    if not name_web:
        frappe.throw(_("Tên không được để trống"), frappe.DoesNotExistError)

    frappe.db.set_value('MBW Client Website', name, 'name_web', name_web)

    return name


@frappe.whitelist()
def set_primary_client_website(name):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("My website not found"), frappe.DoesNotExistError)

    doc = frappe.get_doc('MBW Client Website', name)
    doc.type_web = 'Bản chính'
    doc.save()

    return name


@frappe.whitelist()
def update_published_client_website(name, published):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("My website not found"), frappe.DoesNotExistError)

    doc = frappe.get_doc('MBW Client Website', name)
    doc.published = published
    doc.save()

    return name


@frappe.whitelist()
def update_edit_client_website(name):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("My website not found"), frappe.DoesNotExistError)

    frappe.db.set_value('MBW Client Website', name, 'edit', 1)
    existing_list = frappe.db.sql(
        '''UPDATE `tabMBW Client Website` SET edit=0 WHERE name!="{web_name}" AND edit=1'''.format(web_name=name))
    frappe.db.commit()

    return name


@frappe.whitelist()
def delete_client_website(name):
    if not frappe.db.exists({"doctype": "MBW Client Website", "name": name}):
        frappe.throw(_("My website not found"), frappe.DoesNotExistError)

    frappe.delete_doc('MBW Client Website', name)
    return name
