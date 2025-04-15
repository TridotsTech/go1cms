import frappe
from frappe import _
from go1_cms.api.common import (
    update_fields_page
)
from go1_cms.api.wrapper_api import (
    check_user_admin
)

TYPE_TEMPLATE = {
    'Website giới thiệu': 1,
    'Website tuyển dụng': 2,
    'Website bán hàng dạng liên hệ đặt hàng': 3,
    'Website bán hàng dạng liên hệ đặt hàng và tuyển dụng': 4,
    'Website bán hàng có giỏ hàng': 5
}


@frappe.whitelist()
@check_user_admin
def get_setup():
    try:
        cms_settings = frappe.get_single('CMS Settings')
        web_edit = frappe.db.get_value(
            'MBW Client Website', {"edit": 1}, ['type_template'], as_dict=1)
        active_email = TYPE_TEMPLATE[web_edit.type_template] if web_edit else 0

        fields_cp = []
        # domain
        fields_domain = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Domain',
            'fields': [
                {
                    'field_label': _('Use a different domain'),
                    'field_key': 'use_other_domain',
                    'label_input': _('Use'),
                    'content': cms_settings.use_other_domain == 1,
                    'field_type': 'checkbox',
                    'allow_edit': True,
                    'show_edit': True,
                },
                {
                    'field_label': _('Domain'),
                    'field_key': 'domain',
                    'field_type': 'Data',
                    'content': cms_settings.domain,
                    'allow_edit': True,
                    'show_edit': cms_settings.use_other_domain == 1,
                }
            ],
            'name': 'domain'
        }
        fields_cp.append(fields_domain)

        # email system
        fields_email = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': _('Notification email to admin'),
            'fields': [
                {
                    'field_label': _('Sender email'),
                    'field_key': 'system_email',
                    'field_type': 'Link',
                    'content': cms_settings.system_email,
                    'allow_edit': True,
                    'show_edit': True,
                    'doctype': "Email Account",
                    'filters': {},
                    'actions': [
                        '/app/email-account/',
                        'new-email-account',
                        cms_settings.system_email or ''
                    ]
                },
                {
                    'field_label': _('Receive email notifications'),
                    'field_key': 'allow_send_email_contact',
                    'label_input': _('Allow'),
                    'content': cms_settings.allow_send_email_contact == 1,
                    'field_type': 'checkbox',
                    'allow_edit': True,
                    'show_edit': True,
                    'description': '<strong>' + _('Receive emails in the following cases') + ':</strong> ' + _('when there is a new contact, a new job application, a new order, or a new account registration.')
                },
                {
                    'field_label': _('Email notification recipient list'),
                    'field_key': 'list_email_receipt',
                    'field_type': 'textarea',
                    'content': cms_settings.list_email_receipt,
                    'allow_edit': True,
                    'show_edit': cms_settings.allow_send_email_contact == 1,
                    'placeholder': "`test@gmail.com;demo@gmail.com` or `test@gmail.com; demo@gmail.com`",
                    'description': _('Each email should be separated by `;`.')
                },
                {
                    'field_label': _('Email template for new contact (*)'),
                    'field_key': 'ad_email_temp_new_contact',
                    'field_type': 'Link',
                    'content': cms_settings.ad_email_temp_new_contact,
                    'allow_edit': True,
                    'show_edit': True,
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.ad_email_temp_new_contact or ''
                    ],
                },
                {
                    'field_label': _('Email template for new job application (*)'),
                    'field_key': 'ad_email_temp_new_cv_apply',
                    'field_type': 'Link',
                    'content': cms_settings.ad_email_temp_new_cv_apply,
                    'allow_edit': active_email in [2, 4],
                    'show_edit': active_email in [2, 4],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.ad_email_temp_new_cv_apply or ''
                    ],
                },
                {
                    'field_label': _('Email template for new order (*)'),
                    'field_key': 'ad_email_temp_new_order',
                    'field_type': 'Link',
                    'content': cms_settings.ad_email_temp_new_order,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.ad_email_temp_new_order or ''
                    ],
                },
                {
                    'field_label': _('Email template for new account registration (*)'),
                    'field_key': 'ad_email_temp_new_account',
                    'field_type': 'Link',
                    'content': cms_settings.ad_email_temp_new_account,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.ad_email_temp_new_account or ''
                    ],
                },
            ],
            'name': 'email1'
        }
        fields_cp.append(fields_email)
        # email customer
        fields_email = {
            'allow_edit':  active_email in [5],
            'show_edit': active_email in [5],
            'section_title': _('Customer notification email'),
            'fields': [
                {
                    'field_label': _('Sender email'),
                    'field_key': 'cskh_email',
                    'field_type': 'Link',
                    'content': cms_settings.cskh_email,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Account",
                    'filters': {},
                    'actions': [
                        '/app/email-account/',
                        'new-email-account',
                        cms_settings.cskh_email or ''
                    ]
                },
                {
                    'field_label': _('Send email notifications'),
                    'field_key': 'allow_send_email_customer',
                    'label_input': _('Allow'),
                    'content': cms_settings.allow_send_email_customer == 1,
                    'field_type': 'checkbox',
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'description': '<strong>' + _('Send emails in the following cases') + ':</strong> ' + _('when a new order is placed, when the order is being delivered, when the order is completed, when the order is cancelled, and when an account is registered.')
                },
                {
                    'field_label': _('Email template for new order placement (*)'),
                    'field_key': 'cus_email_temp_new_order',
                    'field_type': 'Link',
                    'content': cms_settings.cus_email_temp_new_order,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.cus_email_temp_new_order or ''
                    ],
                },
                {
                    'field_label': _('Email template for order in delivery (*)'),
                    'field_key': 'cus_email_temp_delivery_order',
                    'field_type': 'Link',
                    'content': cms_settings.cus_email_temp_delivery_order,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.cus_email_temp_delivery_order or ''
                    ],
                },
                {
                    'field_label': _('Email template for order completion (*)'),
                    'field_key': 'cus_email_temp_order_success',
                    'field_type': 'Link',
                    'content': cms_settings.cus_email_temp_order_success,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.cus_email_temp_order_success or ''
                    ],
                },
                {
                    'field_label': _('Email template for order cancellation (*)'),
                    'field_key': 'cus_email_temp_cancel_order',
                    'field_type': 'Link',
                    'content': cms_settings.cus_email_temp_cancel_order,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.cus_email_temp_cancel_order or ''
                    ],
                },
                {
                    'field_label': _('Email template for account registration (*)'),
                    'field_key': 'cus_email_temp_new_account',
                    'field_type': 'Link',
                    'content': cms_settings.cus_email_temp_new_account,
                    'allow_edit': active_email in [5],
                    'show_edit': active_email in [5],
                    'doctype': "Email Template",
                    'filters': {},
                    'actions': [
                        '/app/email-template/',
                        'new-email-template',
                        cms_settings.cus_email_temp_new_account or ''
                    ],
                },
            ],
            'name': 'email2'
        }
        fields_cp.append(fields_email)

        # sync leads
        description = {
            'msg': '',
            'type': 'normal'
        }
        if 'crm' not in frappe.get_installed_apps():
            description = {
                'msg': _('Please install the `CRM` app to use this feature.'),
                'type': 'warn'
            }

        fields_sync = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': _('Sync contacts to Lead (CRM App)'),
            'fields': [
                {
                    'field_label': _('Allow synchronization'),
                    'field_key': 'sync_lead_data',
                    'label_input': _('Allow'),
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
            frappe.throw(_('An error has occurred'))


@frappe.whitelist()
@check_user_admin
def update_setup(data):
    try:
        # update field web theme
        data_update = update_fields_page(data)

        if data_update:
            frappe.db.set_value('CMS Settings', 'CMS Settings', data_update)

        return {'name': 'CMS Settings'}
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except frappe.DoesNotExistError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex), frappe.DoesNotExistError)
    except Exception as ex:
        frappe.throw(_("An error has occurred"))
