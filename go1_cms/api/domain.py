import frappe
from frappe import _
from go1_cms.api.common import (
    update_fields_page
)

# from go1_cms.api.website.jobs import (
#     get_filter_job,
#     get_all_job
# )


@frappe.whitelist()
def get_setup():
    try:
        cms_settings = frappe.get_single('CMS Settings')

        fields_cp = []
        # domain
        fields_logo = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Cài đặt website',
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
            'name': 'logo-2'
        }
        fields_cp.append(fields_logo)

        return {'fields_cp': fields_cp, 'docname': 'CMS Settings'}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Lỗi hệ thống')


@frappe.whitelist()
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
            frappe.throw('Lỗi hệ thống')
