import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_section_content
)

FIELD_TYPE_JSON = ["List", 'Button']


@frappe.whitelist()
def get_info_page(name):
    web_item = frappe.get_doc('MBW Client Website Item', name)
    if not web_item:
        frappe.throw(_("Page not found"), frappe.DoesNotExistError)
    web_edit = frappe.get_last_doc('MBW Client Website', filters={"edit": 1})
    web_page = frappe.get_doc('Web Page Builder', web_item.page_id)

    # get field section in component
    fields_st_cp = []
    for item in web_page.web_section:
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
                if field.get('fields_json'):
                    field['fields_json'] = json.loads(field['fields_json'])
                if field.get('content'):
                    field['content'] = json.loads(field['content']) or []
                    if field.get('field_type') == "List":
                        for item_f in field['fields_json']:
                            for item_ct in field['content']:
                                item_ct['upload_file_image_' +
                                        item_f.get('field_key')] = None

                if field.get('field_type') == "Button" and field.get('content'):
                    f_json = []
                    idx_sc = 1
                    for k in field['content'].keys():
                        field_label = 'Văn bản nút' if k == 'btn_text' else 'Link'
                        f_json.append({
                            "field_key": k,
                            "field_label": field_label,
                            "field_type": "Text",
                            "idx": idx_sc
                        })
                        idx_sc += 1
                    field['fields_json'] = f_json

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
    fields_page = {
        'allow_edit':  True,
        'section_title': 'SEO',
        'fields': [
            {
                'field_label': 'Thẻ tiêu đề',
                'field_key': 'meta_title',
                'field_type': 'Data',
                'content': web_page.meta_title,
                'allow_edit': True,
                'upload_file_image': None
            },
            {
                'group_name': 'seo-1',
                'allow_edit': True,
                'fields': [
                    {
                        'field_label': 'Thẻ mô tả',
                        'field_key': 'meta_description',
                        'field_type': 'Small Text',
                        'content': web_page.meta_description,
                        'allow_edit': True,
                        'upload_file_image': None
                    },
                    {
                        'field_label': 'Thẻ từ khóa',
                        'field_key': 'meta_keywords',
                        'field_type': 'Small Text',
                        'content': web_page.meta_keywords,
                        'allow_edit': True,
                        'upload_file_image': None
                    },
                ]
            },
        ],
        'name': 'header-1'
    }
    fields_cp.append(fields_page)

    web_page_info = {
        'name_page': web_item.name_page,
        'doc_page': web_item.page_id
    }
    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'web_page': web_page_info}


@frappe.whitelist()
def update_info_page(data):
    try:
        page_id = None
        if data.get('web_page') and data.get('web_page').get('doc_page'):
            page_id = data.get('web_page').get('doc_page')
        if not page_id:
            frappe.throw(_("Page not found"),
                         frappe.DoesNotExistError)

        web_edit = frappe.get_last_doc(
            'MBW Client Website', filters={"edit": 1})
        web_page = frappe.get_doc('Web Page Builder', page_id)

        if not web_edit or not web_page:
            frappe.throw(_("Page not found"),
                         frappe.DoesNotExistError)

        # update field section page
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

        # reload page
        web_page.reload()

        # update field page
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
            frappe.db.set_value('Web Page Builder',
                                web_page.name, data_update)

        web_page.reload()
        web_page.save()

        return {'name': web_page.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Lỗi hệ thống')
