import frappe
from frappe import _


@frappe.whitelist()
def get_setup():
    try:
        web_edit = frappe.get_all(
            "MBW Client Website",
            filters={"edit": 1},
            fields=["web_theme"]
        )
        if not web_edit or not frappe.db.exists("Web Theme", web_edit[0].web_theme):
            frappe.throw(_("Web Theme not found"), frappe.DoesNotExistError)

        web_themes = frappe.db.get_all(
            "Web Theme",
            filters={'name': web_edit[0].web_theme},
            fields=['name', 'website_logo', 'secondary_logo',
                    'mobile_logo', 'secondary_mobile_logo', 'favicon']
        )
        web_theme = web_themes[0]

        fields_cp = []
        # logo website
        fields_favicon = {
            'allow_edit':  True,
            'section_title': 'Icon website',
            'fields': [
                {
                    'field_label': 'Favicon (32 x 32px)',
                    'field_key': 'favicon',
                    'field_type': 'Attach',
                    'content': web_theme.favicon,
                    'allow_edit': True,
                    'upload_file_image': None,
                    'classSize': True,
                },

            ],
            'name': 'logo-1'
        }
        fields_cp.append(fields_favicon)

        fields_logo = {
            'allow_edit':  True,
            'section_title': 'Logo website',
            'fields': [
                {
                    'field_label': 'Logo chính (192 x 192px)',
                    'field_key': 'website_logo',
                    'field_type': 'Attach',
                    'content': web_theme.website_logo,
                    'allow_edit': True,
                    'upload_file_image': None
                },
                {
                    'field_label': 'Logo phụ (192 x 192px)',
                    'field_key': 'secondary_logo',
                    'field_type': 'Attach',
                    'content': web_theme.secondary_logo,
                    'allow_edit': True,
                    'upload_file_image': None
                },
                {
                    'field_label': 'Logo mobile chính (192 x 192px)',
                    'field_key': 'mobile_logo',
                    'field_type': 'Attach',
                    'content': web_theme.mobile_logo,
                    'allow_edit': True,
                    'upload_file_image': None
                },
                {
                    'field_label': 'Logo mobile phụ (192 x 192px)',
                    'field_key': 'secondary_mobile_logo',
                    'field_type': 'Attach',
                    'content': web_theme.secondary_mobile_logo,
                    'allow_edit': True,
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
        web_edit = frappe.get_all(
            "MBW Client Website",
            filters={"edit": 1},
            fields=["web_theme"]
        )
        if not web_edit or not frappe.db.exists("Web Theme", web_edit[0].web_theme):
            frappe.throw(_("Web Theme not found"), frappe.DoesNotExistError)

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
            frappe.db.set_value('Web Theme',
                                web_edit[0].web_theme, data_update)

        web_theme = frappe.get_doc('Web Theme', web_edit[0].web_theme)
        web_theme.save(ignore_permissions=True)

        return {'name': web_theme.name}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Lỗi hệ thống')
