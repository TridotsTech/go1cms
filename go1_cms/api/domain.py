import frappe
from frappe import _
from go1_cms.api.common import (
    update_fields_page,
    create_file_template,
    handle_write_file_multiple_doctype_template,
)


@frappe.whitelist()
def get_setup():
    # create_file_template()
    # handle_write_file_multiple_doctype_template()

    # a = frappe.get_doc('My Demo').as_dict().get('r', 123)
    # b = frappe.db.get_single_value("My Demo", "r")

    # print(a, type(a))
    # print(b, type(b))
    # frappe.db.set_value('Demo', 'Demo', 'is_update', 1)
    # frappe.db.commit()
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
