import frappe
from frappe import _
from go1_cms.api.common import (
    handle_write_multiple_files_web_template
)

from go1_cms.go1_cms.after_install import (
    after_install
)
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def create_file_json():
    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    if developer_mode == 0:
        frappe.throw(_("Không thể thực hiện"), frappe.PermissionError)

    handle_write_multiple_files_web_template()
    return {'msg': "Done"}


@frappe.whitelist()
@check_user_admin
def update_from_json():
    developer_mode = frappe.db.get_single_value(
        'CMS Settings', 'developer_mode')
    if developer_mode == 0:
        frappe.throw(_("Không thể thực hiện"), frappe.PermissionError)

    # after_install()
    return {'msg': "Done"}
