import frappe
from frappe import _


@frappe.whitelist()
def get_info_domain():
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
def update_info_domain(data):
    try:
        # update field web theme
        data_update = {}
        if data.get('fields_cp') and type(data.get('fields_cp')) == list:
            for field_cp in data.get('fields_cp'):
                if field_cp.get('allow_edit') and field_cp.get('fields'):
                    for field in field_cp.get('fields'):
                        if field.get('allow_edit'):
                            if field.get('group_name'):
                                for f in field.get('fields'):
                                    data_update[f.get('field_key')] = f.get(
                                        'content')
                            else:
                                data_update[field.get('field_key')] = field.get(
                                    'content')

        if data_update:
            frappe.db.set_value('CMS Settings', 'CMS Settings', data_update)

        return {'name': 'CMS Settings'}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Lỗi hệ thống')
