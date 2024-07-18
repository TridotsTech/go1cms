import frappe
from frappe import _
from go1_cms.api.common import (
    create_file_template,
    handle_write_file_multiple_doctype_template
)

from go1_cms.go1_cms.after_install import (
    after_install
)


@frappe.whitelist()
def create_file_json():
    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    if developer_mode == 0:
        frappe.throw(_("Không thể thực hiện"), frappe.PermissionError)

    create_file_template()
    handle_write_file_multiple_doctype_template()
    return {'msg': "Done"}


@frappe.whitelist()
def update_from_json():
    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    if developer_mode == 0:
        frappe.throw(_("Không thể thực hiện"), frappe.PermissionError)

    after_install()
    return {'msg': "Done"}
