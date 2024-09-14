import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_field_section_component,
    update_fields_page_section,
    update_fields_page
)


@frappe.whitelist()
def get_info_footer_component():
    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name', 'footer_component', 'route_web'], as_dict=1)
    if not web_edit or not web_edit.footer_component:
        frappe.throw(_("Footer not found"), frappe.DoesNotExistError)
    if not frappe.db.exists("Footer Component", web_edit.footer_component):
        frappe.throw(_("Footer not found"), frappe.DoesNotExistError)

    footer_component = frappe.get_doc(
        "Footer Component", web_edit.footer_component)

    # get field section in component
    fields_st_cp = get_field_section_component(
        web_edit, footer_component.web_section)

    # fields component
    fields_cp = []
    # footer
    fields_footer = {
        'allow_edit':  True,
        'show_edit': True if footer_component.footer_bg_image else False,
        'section_title': 'Thiết kế',
        'image': None,
        'show_prv_image': False,
        'fields': [
            {
                'field_label': 'Ảnh nền',
                'field_key': 'footer_bg_image',
                'field_type': 'upload_image',
                'content': footer_component.footer_bg_image,
                'allow_edit': True if footer_component.footer_bg_image else False,
                'show_edit': True,
                'upload_file_image': None
            }
        ],
        'name': 'footer-0'
    }
    fields_cp.append(fields_footer)

    # copyright
    fields_copyright = {
        'allow_edit':  True,
        'show_edit': footer_component.enable_copyright == 1,
        'section_title': 'Nội dung bản quyền',
        'image': footer_component.image_copyright,
        'show_prv_image': True,
        'fields': [
            {
                'field_label': 'Nội dung cột 1',
                'field_key': 'cp_fc_content',
                'field_type': 'Small Text',
                'content': footer_component.cp_fc_content,
                'allow_edit': True,
                'show_edit': footer_component.fc_ct_type == 'Custom'
            },
            {
                'field_label': 'Nội dung cột 2',
                'field_key': 'cp_sc_content',
                'field_type': 'Small Text',
                'content': footer_component.cp_sc_content,
                'allow_edit': True,
                'show_edit': footer_component.sc_ct_type == 'Custom'
            }
        ],
        'name': 'footer-1'
    }
    fields_cp.append(fields_copyright)

    web_page = {
        'route': web_edit.route_web
    }

    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'docname': footer_component.name, 'web_page': web_page}


@frappe.whitelist()
def update_info_footer_component(data):
    try:
        web_edit = frappe.db.get_value(
            'MBW Client Website', {"edit": 1}, ['name', 'footer_component'], as_dict=1)
        if not web_edit or not web_edit.footer_component:
            frappe.throw(_("Footer not found"),
                         frappe.DoesNotExistError)
        if not frappe.db.exists("Footer Component", web_edit.footer_component):
            frappe.throw(_("Footer not found"),
                         frappe.DoesNotExistError)

        footer_component = frappe.get_doc(
            "Footer Component", web_edit.footer_component)

        # update field section footer component
        update_fields_page_section(data)

        # reload footer component
        footer_component.reload()

        # update field footer component
        data_update = update_fields_page(data)

        if data_update:
            frappe.db.set_value('Footer Component',
                                footer_component.name, data_update)

        footer_component.reload()
        footer_component.save()

        return {'name': footer_component.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Lỗi hệ thống')
