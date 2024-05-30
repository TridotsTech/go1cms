import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_section_content
)

FIELD_TYPE_JSON = ["List", 'Button']


@frappe.whitelist()
def get_info_footer_component():
    web_edit = frappe.get_last_doc('MBW Client Website', filters={"edit": 1})
    if not web_edit or not web_edit.footer_component:
        frappe.throw(_("Footer component not found"), frappe.DoesNotExistError)
    if not frappe.db.exists("Footer Component", web_edit.footer_component):
        frappe.throw(_("Footer component not found"), frappe.DoesNotExistError)

    footer_component = frappe.get_doc(
        "Footer Component", web_edit.footer_component)

    # get field section in component
    fields_st_cp = []
    for item in footer_component.web_section:
        info_item = get_section_content(item.section, 'Data')
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
    # copyright
    fields_copyright = {
        'allow_edit':  footer_component.enable_copyright == 1,
        'label': 'Nội dung bản quyền',
        'fields': [
            {
                 'field_label': 'Nội dung cột 1',
                 'field_key': 'cp_fc_content',
                'field_type': 'Small Text',
                'content': footer_component.cp_fc_content,
                'allow_edit': footer_component.fc_ct_type == 'Custom',
                'upload_file_image': None
            },
            {
                'field_label': 'Nội dung cột 2',
                'field_key': 'cp_sc_content',
                'field_type': 'Small Text',
                'content': footer_component.cp_sc_content,
                'allow_edit': footer_component.sc_ct_type == 'Custom',
                'upload_file_image': None
            }
        ],
        'name': 'footer-1'
    }

    fields_cp.append(fields_copyright)

    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'docname': footer_component.name}


@frappe.whitelist()
def update_info_footer_component(data):
    try:
        web_edit = frappe.get_last_doc(
            'MBW Client Website', filters={"edit": 1})
        if not web_edit or not web_edit.footer_component:
            frappe.throw(_("Footer component not found"),
                         frappe.DoesNotExistError)
        if not frappe.db.exists("Footer Component", web_edit.footer_component):
            frappe.throw(_("Footer component not found"),
                         frappe.DoesNotExistError)

        footer_component = frappe.get_doc(
            "Footer Component", web_edit.footer_component)

        # update field section footer component
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

        # reload footer component
        footer_component.reload()

        # update field footer component
        data_update = {}
        if data.get('fields_cp') and type(data.get('fields_cp')) == list:
            for field_cp in data.get('fields_cp'):
                if field_cp.get('allow_edit') and field_cp.get('fields'):
                    for field in field_cp.get('fields'):
                        if field.get('allow_edit'):
                            data_update[field.get('field_key')] = field.get(
                                'content')

        if data_update:
            frappe.db.set_value('Footer Component',
                                footer_component.name, data_update)

        footer_component.reload()
        footer_component.save()

        return {'name': footer_component.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Lỗi hệ thống')
