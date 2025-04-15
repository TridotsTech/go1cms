import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_field_section_component,
    update_fields_page_section,
    update_fields_page
)
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_info_header_component():
    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name', 'header_component', 'route_web'], as_dict=1)
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
    # get field
    fields_btn = {
        'allow_edit':  True,
        'show_edit': True,
        'section_title': 'Button information',
        'image': header_component.image_btn,
        'show_prv_image': True,
        'fields': [
            {
                'group_name': 'group 1',
                'section_title': 'First button',
                'show_edit': header_component.active_button == 1 and header_component.call_to_action_button == 1,
                'fields': [
                    {
                        'field_label': 'Label',
                        'field_key': 'button_text',
                        'field_type': 'Data',
                        'content': header_component.button_text,
                        'allow_edit':  True,
                        'show_edit': header_component.show_btn_text == 1
                    },
                    {
                        'field_label': 'Button sublabel',
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
                        'field_label': 'Redirect link',
                        'field_key': 'link_target',
                        'field_type': 'Select',
                        'content': header_component.link_target,
                        'allow_edit':  True,
                        'show_edit': header_component.use_action == 'link',
                        'options': [
                            {'label': _('Current page'), 'value': '_self'},
                            {'label': _('New page'), 'value': '_blank'}
                        ]
                    },
                ]
            },
            {
                'group_name': 'group 2',
                'section_title': 'Second button',
                'show_edit': header_component.active_button_2 == 1 and header_component.call_to_action_button == 1,
                'fields': [
                    {
                        'field_label': _('Label'),
                        'field_key': 'button_text_2',
                        'field_type': 'Data',
                        'content': header_component.button_text_2,
                        'allow_edit':  True,
                        'show_edit': header_component.show_btn_text_2 == 1
                    },
                    {
                        'field_label': _('Button sublabel'),
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
                        'field_label': _('Redirect link'),
                        'field_key': 'link_target_2',
                        'field_type': 'Select',
                        'content': header_component.link_target_2,
                        'allow_edit':  True,
                        'show_edit': header_component.use_action_2 == 'link',
                        'options': [
                            {'label': _('Current page'), 'value': '_self'},
                            {'label': _('New page'), 'value': '_blank'}
                        ]
                    },
                ],
            },
            {
                'group_name': 'group 3',
                'section_title': 'Third button',
                'show_edit': header_component.active_button_3 == 1 and header_component.call_to_action_button == 1,
                'fields': [
                    {
                        'field_label': _('Label'),
                        'field_key': 'button_text_3',
                        'field_type': 'Data',
                        'content': header_component.button_text_3,
                        'allow_edit':  True,
                        'show_edit': header_component.show_btn_text_3 == 1
                    },
                    {
                        'field_label': _('Button sublabel'),
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
                        'field_label': _('Redirect link'),
                        'field_key': 'link_target_3',
                        'field_type': 'Select',
                        'content': header_component.link_target_3,
                        'allow_edit':  True,
                        'show_edit': header_component.use_action_3 == 'link',
                        'options': [
                            {'label': _('Current page'), 'value': '_self'},
                            {'label': _('New page'), 'value': '_blank'}
                        ]
                    },
                ],
            },
            {
                'group_name': 'group 4',
                'section_title': 'Fourth button',
                'show_edit': header_component.active_button_4 == 1 and header_component.call_to_action_button == 1,
                'fields': [
                    {
                        'field_label': _('Label'),
                        'field_key': 'button_text_4',
                        'field_type': 'Data',
                        'content': header_component.button_text_4,
                        'allow_edit':  True,
                        'show_edit': header_component.show_btn_text_4 == 1
                    },
                    {
                        'field_label': _('Button sublabel'),
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
                        'field_label': _('Redirect link'),
                        'field_key': 'link_target_4',
                        'field_type': 'Select',
                        'content': header_component.link_target_4,
                        'allow_edit':  True,
                        'show_edit': header_component.use_action_4 == 'link',
                        'options': [
                            {'label': _('Current page'), 'value': '_self'},
                            {'label': _('New page'), 'value': '_blank'}
                        ]
                    },
                ],
            }
        ],
        'name': 'header-1'
    }

    for f in fields_btn.get('fields'):
        if f.get('show_edit'):
            fields_cp.append(fields_btn)
            break

    web_page = {
        'route': web_edit.route_web
    }

    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'docname': header_component.name, 'web_page': web_page}


@frappe.whitelist()
@check_user_admin
def update_info_header_component(data):
    try:
        web_edit = frappe.db.get_value(
            'MBW Client Website', {"edit": 1}, ['name', 'header_component'], as_dict=1)
        if not web_edit or not web_edit.header_component:
            frappe.throw(_("Header not found"), frappe.DoesNotExistError)
        if not frappe.db.exists("Header Component", web_edit.header_component):
            frappe.throw(_("Header not found"), frappe.DoesNotExistError)

        header_component = frappe.get_doc(
            "Header Component", web_edit.header_component)

        # update field section header component
        update_fields_page_section(data)

        # reload header component
        header_component.reload()

        # update field header component
        data_update = update_fields_page(data)

        if data_update:
            frappe.db.set_value('Header Component',
                                header_component.name, data_update)

        header_component.reload()
        header_component.save()

        return {'name': header_component.name}
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except frappe.DoesNotExistError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex), frappe.DoesNotExistError)
    except Exception as ex:
        frappe.throw(_("An error has occurred"))
