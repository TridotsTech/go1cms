import frappe
from frappe import _
from pypika import Criterion
from frappe.model.document import get_controller


@frappe.whitelist()
def get_client_websites():
    filters = {}
    doctype = "MBW Client Website"
    columns = []
    rows_in_list = []
    rows = []
    order_by = "modified desc"

    _list = get_controller(doctype)
    if hasattr(_list, "default_list_data"):
        columns = _list.default_list_data().get("columns")
        rows = _list.default_list_data().get("rows")

    # check if rows has all keys from columns if not add them
    for column in columns:
        if column.get("key") not in rows:
            rows.append(column.get("key"))
        column["label"] = _(column.get("label"))

        if column.get("key") == "_liked_by" and column.get("width") == "10rem":
            column["width"] = "50px"
    rows_in_list = [row for row in rows]
    rows = [row for row in rows if row not in ['action_button']]

    data = frappe.db.get_all(
        doctype,
        fields=rows,
        filters=filters,
        order_by=order_by
    ) or []

    return {
        "data": data,
        "columns": columns,
        "rows": rows_in_list,
        "total_count": len(frappe.get_all(doctype, filters=filters)),
        "row_count": len(data),
    }


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
