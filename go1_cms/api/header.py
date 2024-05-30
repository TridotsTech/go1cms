import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_section_content
)

FIELD_TYPE_JSON = ["List", 'Button']


@frappe.whitelist()
def get_info_header_component():
    web_edit = frappe.get_last_doc('MBW Client Website', filters={"edit": 1})
    if not web_edit or not web_edit.header_component:
        frappe.throw(_("Header component not found"), frappe.DoesNotExistError)
    if not frappe.db.exists("Header Component", web_edit.header_component):
        frappe.throw(_("Header component not found"), frappe.DoesNotExistError)

    header_component = frappe.get_doc(
        "Header Component", web_edit.header_component)

    # get field section in component
    fields_st_cp = []
    for item in header_component.web_section:
        info_item = get_section_content(item.section, 'Data')
        if item.section_name in ['Header Logo', 'Header Button']:
            info_item['allow_edit'] = False
        else:
            info_item['allow_edit'] = True
        d = {}
        fields_new = []
        if info_item.get('section_type') == "Menu":
            info_item['fields_ps'] = [
                {
                    'field_label': 'Menu',
                    'field_key': 'menu',
                    'field_type': 'Link',
                    'content': info_item.get('menu'),
                    'allow_edit': True,
                    'upload_file_image': None,
                    'doctype': "Menu",
                    'filters': {
                        'id_client_website': web_edit.name
                    }

                }
            ]

        for field in info_item['fields']:
            field['allow_edit'] = True
            field['upload_file_image'] = None
            if field.get('field_type') in FIELD_TYPE_JSON:
                field['content'] = json.loads(field['content'])
                field['fields_json'] = json.loads(field['fields_json'])

            if field.get('group_name'):
                if not d.get(str(field.get('group_name'))):
                    d[str(field.get('group_name'))] = []
                d[str(field.get('group_name'))].append(field)
            else:
                fields_new.append(field)

        for k, v in d.items():
            obj = {
                'group_name': k,
                'fields': v
            }
            fields_new.append(obj)

        info_item['fields'] = fields_new
        fields_st_cp.append(info_item)

    # fields component
    fields_cp = []
    # get field group button 1
    fields_btn_1 = {
        'allow_edit':  header_component.active_button == 1 and header_component.call_to_action_button == 1,
        'label': 'Thông tin nút 1',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text',
                'field_type': 'Data',
                'content': header_component.button_text,
                'allow_edit': header_component.show_btn_text == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'sub_text',
                'field_type': 'Data',
                'content': header_component.sub_text,
                'allow_edit': header_component.show_sub_text == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link',
                'field_type': 'Data',
                'content': header_component.button_link,
                'allow_edit': header_component.use_action == 'link',
                'upload_file_image': None
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target',
                'field_type': 'Select',
                'content': header_component.link_target,
                'allow_edit': header_component.use_action == 'link',
                'upload_file_image': None,
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
        'allow_edit':  header_component.active_button_2 == 1 and header_component.call_to_action_button == 1,
        'label': 'Thông tin nút 2',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text_2',
                'field_type': 'Data',
                'content': header_component.button_text_2,
                'allow_edit': header_component.show_btn_text_2 == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'sub_text_2',
                'field_type': 'Data',
                'content': header_component.sub_text_2,
                'allow_edit': header_component.show_sub_text_2 == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link_2',
                'field_type': 'Data',
                'content': header_component.button_link_2,
                'allow_edit': header_component.use_action_2 == 'link',
                'upload_file_image': None
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target_2',
                'field_type': 'Select',
                'content': header_component.link_target_2,
                'allow_edit': header_component.use_action_2 == 'link',
                'upload_file_image': None,
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
        'allow_edit':  header_component.active_button_3 == 1 and header_component.call_to_action_button == 1,
        'label': 'Thông tin nút 1',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text_3',
                'field_type': 'Data',
                'content': header_component.button_text_3,
                'allow_edit': header_component.show_btn_text_3 == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'sub_text_3',
                'field_type': 'Data',
                'content': header_component.sub_text_3,
                'allow_edit': header_component.show_sub_text_3 == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link_3',
                'field_type': 'Data',
                'content': header_component.button_link_3,
                'allow_edit': header_component.use_action_3 == 'link',
                'upload_file_image': None
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target_3',
                'field_type': 'Select',
                'content': header_component.link_target_3,
                'allow_edit': header_component.use_action_3 == 'link',
                'upload_file_image': None,
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
        'allow_edit':  header_component.active_button_4 == 1 and header_component.call_to_action_button == 1,
        'label': 'Thông tin nút 1',
        'fields': [
            {
                'field_label': 'Văn bản nút',
                'field_key': 'button_text_4',
                'field_type': 'Data',
                'content': header_component.button_text_4,
                'allow_edit': header_component.show_btn_text_4 == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Văn bản phụ nút',
                'field_key': 'button_text_4',
                'field_type': 'Data',
                'content': header_component.button_text_4,
                'allow_edit': header_component.show_sub_text_4 == 1,
                'upload_file_image': None
            },
            {
                'field_label': 'Link',
                'field_key': 'button_link_4',
                'field_type': 'Data',
                'content': header_component.button_link_4,
                'allow_edit': header_component.use_action_4 == 'link',
                'upload_file_image': None
            },
            {
                'field_label': 'Mục tiêu Link',
                'field_key': 'link_target_4',
                'field_type': 'Select',
                'content': header_component.link_target_4,
                'allow_edit': header_component.use_action_4 == 'link',
                'upload_file_image': None,
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
        web_edit = frappe.get_last_doc(
            'MBW Client Website', filters={"edit": 1})
        if not web_edit or not web_edit.header_component:
            frappe.throw(_("Header component not found"),
                         frappe.DoesNotExistError)
        if not frappe.db.exists("Header Component", web_edit.header_component):
            frappe.throw(_("Header component not found"),
                         frappe.DoesNotExistError)

        header_component = frappe.get_doc(
            "Header Component", web_edit.header_component)

        # update field section header component
        if data.get('fields_st_cp') and type(data.get('fields_st_cp')) == list:
            for fcp in data.get('fields_st_cp'):
                if fcp.get("allow_edit") and fcp.get('fields'):
                    for field in fcp.get('fields'):
                        if field.get('group_name'):
                            for f in field.get('fields'):
                                if f.get("allow_edit"):
                                    # update Section Content
                                    content = f.get('content')
                                    if f.get('field_type') in FIELD_TYPE_JSON:
                                        content = json.dumps(f.get('content'))
                                    frappe.db.set_value('Section Content', f.get('name'), {
                                        'content': content
                                    })
                        else:
                            if field.get("allow_edit"):
                                # update Section Content
                                content = field.get('content')
                                if field.get('field_type') in FIELD_TYPE_JSON:
                                    content = json.dumps(field.get('content'))
                                frappe.db.set_value('Section Content', field.get('name'), {
                                    'content': content
                                })

                if fcp.get("allow_edit") and fcp.get("fields_ps"):
                    d_update = {}
                    for field in fcp.get('fields_ps'):
                        d_update[field.get('field_key')] = field.get('content')

                    if d_update:
                        frappe.db.set_value(
                            'Page Section', fcp.get('name'), d_update)

        # reload header component
        header_component.reload()

        # update field header component
        data_update = {}
        if data.get('fields_cp') and type(data.get('fields_cp')) == list:
            for field_cp in data.get('fields_cp'):
                if field_cp.get('allow_edit') and field_cp.get('fields'):
                    for field in field_cp.get('fields'):
                        if field.get('allow_edit'):
                            data_update[field.get('field_key')] = field.get(
                                'content')

        if data_update:
            frappe.db.set_value('Header Component',
                                header_component.name, data_update)

        header_component.reload()
        header_component.save()

        return {'name': header_component.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Lỗi hệ thống')
