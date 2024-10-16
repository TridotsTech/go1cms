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
        # domain
        fields_logo = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Domain',
            'fields': [
                {
                    'field_label': 'Sử dụng tên miền khác',
                    'field_key': 'use_other_domain',
                    'label_input': 'Sử dụng',
                    'content': cms_settings.use_other_domain == 1,
                    'field_type': 'checkbox',
                    'allow_edit': True,
                    'show_edit': True,
                },
                {
                    'field_label': 'Tên miền',
                    'field_key': 'domain',
                    'field_type': 'Data',
                    'content': cms_settings.domain,
                    'allow_edit': True,
                    'show_edit': cms_settings.use_other_domain == 1,
                }
            ],
            'name': 'domain'
        }
        fields_cp.append(fields_logo)
        
        # email
        fields_email = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Email',
            'fields': [
                {
                    'field_label': 'Email thông báo hệ thống',
                    'field_key': 'system_email',
                    'field_type': 'Link',
                    'content': cms_settings.system_email,
                    'allow_edit': True,
                    'show_edit': True,
                    'doctype': "Email Account",
                    'filters': {}
                },
                {
                    'field_label': 'Email thông báo khách hàng',
                    'field_key': 'cskh_email',
                    'field_type': 'Link',
                    'content': cms_settings.cskh_email,
                    'allow_edit': True,
                    'show_edit': True,
                    'doctype': "Email Account",
                    'filters': {}
                },
                {
                    'field_label': 'Nhận thông báo email liên hệ',
                    'field_key': 'allow_send_email_contact',
                    'label_input': 'Cho phép',
                    'content': cms_settings.allow_send_email_contact == 1,
                    'field_type': 'checkbox',
                    'allow_edit': True,
                    'show_edit': True,
                    'description': '<strong>Nhận email trong các trường hợp:</strong> có CV tuyển dụng mới, có đơn đặt đơn hàng mới và có đăng ký tài khoản mới'
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
                },
                {
                    'field_label': 'Gửi thông báo email cho khách hàng',
                    'field_key': 'allow_send_email_customer',
                    'label_input': 'Cho phép',
                    'content': cms_settings.allow_send_email_customer == 1,
                    'field_type': 'checkbox',
                    'allow_edit': True,
                    'show_edit': True,
                    'description': '<strong>Gửi email trong các trường hợp:</strong> khi đặt đơn hàng, khi đăng ký tài khoản'
                },
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
