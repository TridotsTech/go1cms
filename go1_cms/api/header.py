import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_field_section_component,
    update_fields_page_section,
    update_fields_page
)


@frappe.whitelist()
def get_info_header_component():
    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name', 'header_component'], as_dict=1)
    if not web_edit or not web_edit.header_component:
        frappe.throw(_("Header not found"), frappe.DoesNotExistError)
    if not frappe.db.exists("Header Component", web_edit.header_component):
        frappe.throw(_("Header not found"), frappe.DoesNotExistError)

    header_component = frappe.get_doc(
        "Header Component", web_edit.header_component)

    # get field section in component
    fields_st_cp = get_field_section_component(
        web_edit, header_component.web_section)

    # fields component
    fields_cp = []
    # get field group button 1
    fields_btn_1 = {
        'allow_edit':  True,
        'show_edit': header_component.active_button == 1 and header_component.call_to_action_button == 1,
        'section_title': 'Thông tin nút 1',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text',
                'field_type': 'Data',
                'content': header_component.button_text,
                'allow_edit':  True,
                'show_edit': header_component.show_btn_text == 1
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'sub_text',
                'field_type': 'Data',
                'content': header_component.sub_text,
                'allow_edit':  True,
                'show_edit': header_component.show_sub_text == 1
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link',
                'field_type': 'Data',
                'content': header_component.button_link,
                'allow_edit':  True,
                'show_edit': header_component.use_action == 'link'
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target',
                'field_type': 'Select',
                'content': header_component.link_target,
                'allow_edit':  True,
                'show_edit': header_component.use_action == 'link',
                'options': [
                    {'label': 'Trang hiện tại', 'value': '_self'},
                    {'label': 'Trang mới', 'value': '_blank'}
                ]
            },
        ],
        'name': 'header-1'
    }
    fields_cp.append(fields_btn_1)
    # get field group button 2
    fields_btn_2 = {
        'allow_edit':  True,
        'show_edit':  header_component.active_button_2 == 1 and header_component.call_to_action_button == 1,
        'section_title': 'Thông tin nút 2',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text_2',
                'field_type': 'Data',
                'content': header_component.button_text_2,
                'allow_edit':  True,
                'show_edit': header_component.show_btn_text_2 == 1
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'sub_text_2',
                'field_type': 'Data',
                'content': header_component.sub_text_2,
                'allow_edit':  True,
                'show_edit': header_component.show_sub_text_2 == 1
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link_2',
                'field_type': 'Data',
                'content': header_component.button_link_2,
                'allow_edit':  True,
                'show_edit': header_component.use_action_2 == 'link'
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target_2',
                'field_type': 'Select',
                'content': header_component.link_target_2,
                'allow_edit':  True,
                'show_edit': header_component.use_action_2 == 'link',
                'options': [
                    {'label': 'Trang hiện tại', 'value': '_self'},
                    {'label': 'Trang mới', 'value': '_blank'}
                ]
            },
        ],
        'name': 'header-2'
    }
    fields_cp.append(fields_btn_2)
    # get field group button 3
    fields_btn_3 = {
        'allow_edit':  True,
        'show_edit':  header_component.active_button_3 == 1 and header_component.call_to_action_button == 1,
        'section_title': 'Thông tin nút 3',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text_3',
                'field_type': 'Data',
                'content': header_component.button_text_3,
                'allow_edit':  True,
                'show_edit': header_component.show_btn_text_3 == 1
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'sub_text_3',
                'field_type': 'Data',
                'content': header_component.sub_text_3,
                'allow_edit':  True,
                'show_edit': header_component.show_sub_text_3 == 1
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link_3',
                'field_type': 'Data',
                'content': header_component.button_link_3,
                'allow_edit':  True,
                'show_edit': header_component.use_action_3 == 'link'
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target_3',
                'field_type': 'Select',
                'content': header_component.link_target_3,
                'allow_edit':  True,
                'show_edit': header_component.use_action_3 == 'link',
                'options': [
                    {'label': 'Trang hiện tại', 'value': '_self'},
                    {'label': 'Trang mới', 'value': '_blank'}
                ]
            },
        ],
        'name': 'header-1'
    }
    fields_cp.append(fields_btn_3)
    # get field group button 4
    fields_btn_4 = {
        'allow_edit':  True,
        'show_edit':  header_component.active_button_4 == 1 and header_component.call_to_action_button == 1,
        'section_title': 'Thông tin nút 4',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text_4',
                'field_type': 'Data',
                'content': header_component.button_text_4,
                'allow_edit':  True,
                'show_edit': header_component.show_btn_text_4 == 1
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'button_text_4',
                'field_type': 'Data',
                'content': header_component.button_text_4,
                'allow_edit':  True,
                'show_edit': header_component.show_sub_text_4 == 1
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link_4',
                'field_type': 'Data',
                'content': header_component.button_link_4,
                'allow_edit':  True,
                'show_edit': header_component.use_action_4 == 'link'
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target_4',
                'field_type': 'Select',
                'content': header_component.link_target_4,
                'allow_edit':  True,
                'show_edit': header_component.use_action_4 == 'link',
                'options': [
                    {'label': 'Trang hiện tại', 'value': '_self'},
                    {'label': 'Trang mới', 'value': '_blank'}
                ]
            },
        ],
        'name': 'header-1'
    }
    fields_cp.append(fields_btn_4)

    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'docname': header_component.name}


@frappe.whitelist()
def update_info_header_component(data):
    try:
        web_edit = frappe.db.get_value(
            'MBW Client Website', {"edit": 1}, ['name', 'header_component'], as_dict=1)
        if not web_edit or not web_edit.header_component:
            frappe.throw(_("Header not found"),
                         frappe.DoesNotExistError)
        if not frappe.db.exists("Header Component", web_edit.header_component):
            frappe.throw(_("Header not found"),
                         frappe.DoesNotExistError)

        header_component = frappe.get_doc(
            "Header Component", web_edit.header_component)

        # update field section header component
        update_fields_page_section(data)

        # reload header component
        header_component.reload()

        # update field header component
        data_update = {}
        update_fields_page(data, data_update)

        if data_update:
            frappe.db.set_value('Header Component',
                                header_component.name, data_update)

        header_component.reload()
        header_component.save()

        return {'name': header_component.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Lỗi hệ thống')
