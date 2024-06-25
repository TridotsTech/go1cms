import frappe
from frappe import _
from go1_cms.api.common import (
    update_fields_page
)


@frappe.whitelist()
def get_setup():
    try:
        web_edit = frappe.db.get_value(
            'MBW Client Website', {"edit": 1}, ['web_theme'], as_dict=1)
        if not web_edit or not frappe.db.exists("Web Theme", web_edit.web_theme):
            frappe.throw(_("Web Theme not found"), frappe.DoesNotExistError)

        web_themes = frappe.db.get_all(
            "Web Theme",
            filters={'name': web_edit.web_theme},
            fields=['name', 'website_logo', 'secondary_logo',
                    'mobile_logo', 'secondary_mobile_logo', 'favicon']
        )
        web_theme = web_themes[0]

        fields_cp = []
        # logo website
        fields_favicon = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Website icon',
            'fields': [
                {
                    'field_label': 'Favicon (32 x 32px)',
                    'field_key': 'favicon',
                    'field_type': 'Attach',
                    'content': web_theme.favicon,
                    'allow_edit': True,
                    'show_edit': True,
                    'upload_file_image': None,
                    'classSize': True,
                },

            ],
            'name': 'logo-1'
        }
        fields_cp.append(fields_favicon)

        fields_logo = {
            'allow_edit':  True,
            'show_edit': True,
            'section_title': 'Website logo',
            'fields': [
                {
                    'field_label': 'Logo chính (192 x 192px)',
                    'field_key': 'website_logo',
                    'field_type': 'Attach',
                    'content': web_theme.website_logo,
                    'allow_edit': True,
                    'show_edit': True,
                    'upload_file_image': None
                },
                {
                    'field_label': 'Logo phụ (192 x 192px)',
                    'field_key': 'secondary_logo',
                    'field_type': 'Attach',
                    'content': web_theme.secondary_logo,
                    'allow_edit': True,
                    'show_edit': True,
                    'upload_file_image': None
                },
                {
                    'field_label': 'Logo mobile chính (192 x 192px)',
                    'field_key': 'mobile_logo',
                    'field_type': 'Attach',
                    'content': web_theme.mobile_logo,
                    'allow_edit': True,
                    'show_edit': True,
                    'upload_file_image': None
                },
                {
                    'field_label': 'Logo mobile phụ (192 x 192px)',
                    'field_key': 'secondary_mobile_logo',
                    'field_type': 'Attach',
                    'content': web_theme.secondary_mobile_logo,
                    'allow_edit': True,
                    'show_edit': True,
                    'upload_file_image': None
                },

            ],
            'name': 'logo-2'
        }
        fields_cp.append(fields_logo)

        return {'fields_cp': fields_cp, 'docname': web_theme.name}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Lỗi hệ thống')


@frappe.whitelist()
def update_setup(data):
    try:
        web_edit = frappe.db.get_value(
            'MBW Client Website', {"edit": 1}, ['web_theme'], as_dict=1)
        if not web_edit or not frappe.db.exists("Web Theme", web_edit.web_theme):
            frappe.throw(_("Web Theme not found"), frappe.DoesNotExistError)

        # update field web theme
        data_update = update_fields_page(data)

        if data_update:
            frappe.db.set_value('Web Theme',
                                web_edit.web_theme, data_update)

        web_theme = frappe.get_doc('Web Theme', web_edit.web_theme)
        web_theme.save(ignore_permissions=True)

        return {'name': web_theme.name}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Lỗi hệ thống')
