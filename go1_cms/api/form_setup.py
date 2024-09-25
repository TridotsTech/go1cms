import frappe
from frappe import _
from go1_cms.api.common import (
    update_fields_page
)
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_setup():
    try:
        cms_settings = frappe.get_single('CMS Settings')

        fields_cp = []
        # email
        fields_email = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Nhận email liên hệ',
            'fields': [
                {
                    'field_label': 'Cho phép gửi email',
                    'field_key': 'allow_send_email_contact',
                    'label_input': 'Cho phép',
                    'content': cms_settings.allow_send_email_contact == 1,
                    'field_type': 'checkbox',
                    'allow_edit': True,
                    'show_edit': True,
                },
                {
                    'field_label': 'Danh sách email nhận thông báo',
                    'field_key': 'list_email_receipt',
                    'field_type': 'textarea',
                    'content': cms_settings.list_email_receipt,
                    'allow_edit': True,
                    'show_edit': cms_settings.allow_send_email_contact == 1,
                    'placeholder': "`test@gmail.com;demo@gmail.com` or `test@gmail.com; demo@gmail.com`",
                    'description': "Mỗi email cách nhau bởi dấu `;`."
                }
            ],
            'name': 'email'
        }
        fields_cp.append(fields_email)

        # sync leads
        description = {
            'msg': '',
            'type': 'normal'
        }
        if 'crm' not in frappe.get_installed_apps():
            description = {
                'msg': 'Vui lòng cài đặt thêm app `CRM` để sử dụng tính năng này.',
                'type': 'warn'
            }

        fields_sync = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Đồng bộ liên hệ sang Lead(App CRM)',
            'fields': [
                {
                    'field_label': 'Cho phép đồng bộ',
                    'field_key': 'sync_lead_data',
                    'label_input': 'Cho phép',
                    'content': cms_settings.sync_lead_data == 1,
                    'field_type': 'checkbox',
                    'allow_edit': 'crm' in frappe.get_installed_apps(),
                    'show_edit': True,
                }
            ],
            'description': description,
            'name': 'sync'
        }
        fields_cp.append(fields_sync)

        return {'fields_cp': fields_cp, 'docname': 'CMS Settings'}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Có lỗi xảy ra')


@frappe.whitelist()
@check_user_admin
def update_setup(data):
    try:
        # update field web theme
        data_update = update_fields_page(data)

        if data_update:
            frappe.db.set_value('CMS Settings', 'CMS Settings', data_update)

        return {'name': 'CMS Settings'}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Có lỗi xảy ra')
