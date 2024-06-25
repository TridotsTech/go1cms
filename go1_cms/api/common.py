import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
import json

FIELD_TYPE_JSON = ["List", 'Button']


def copy_header_component(name, sub_name):
    target_doc = None
    doc_header_comp = frappe.new_doc("Header Component")
    doc_header_comp = get_mapped_doc("Header Component", name,	{
        "Header Component": {
            "doctype": "Header Component"
        },
    }, target_doc, ignore_permissions=True)
    doc_header_comp.idx = None
    doc_header_comp.web_section = []
    doc_header_comp.title = doc_header_comp.title + ' ' + sub_name

    web_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": name, "parentfield": "web_section"}, fields=[
        'section', 'section_title', 'section_type', 'content_type', 'allow_update_to_style', 'idx', 'column_index'], order_by="idx")
    web_secs = []
    for x in web_sections:
        target_doc = None
        doc = frappe.new_doc("Page Section")
        doc = get_mapped_doc("Page Section", x.section,	{
            "Page Section": {
                "doctype": "Page Section"
            },
        }, target_doc, ignore_permissions=True)
        if doc.section_type == 'Menu':
            target_doc = None
            doc_menu = frappe.new_doc("Menu")
            doc_menu = get_mapped_doc("Menu", doc.menu,	{
                "Menu": {
                    "doctype": "Menu"
                },
            }, target_doc, ignore_permissions=True)
            # doc_menu.title = doc_menu.title + ' ' + sub_name
            doc_menu.id_parent_copy = doc.menu
            doc_menu.title = doc_menu.title
            doc_menu.id_client_website = sub_name
            doc_menu.save(ignore_permissions=True)
            doc.menu = doc_menu.name
        doc.save(ignore_permissions=True)

        m_page_sec = frappe.new_doc("Mobile Page Section")
        m_page_sec.section_title = x.section_title
        m_page_sec.section_type = x.section_type
        m_page_sec.content_type = x.content_type
        m_page_sec.allow_update_to_style = x.allow_update_to_style
        m_page_sec.idx = x.idx
        m_page_sec.column_index = x.column_index
        m_page_sec.parentfield = "web_section"
        m_page_sec.parenttype = "Header Component"
        m_page_sec.section = doc.name
        web_secs.append(m_page_sec)

    doc_header_comp.web_section = web_secs
    doc_header_comp.save(ignore_permissions=True)
    # frappe.db.commit()
    return doc_header_comp.name


def copy_footer_component(name, sub_name):
    target_doc = None
    doc_footer_comp = frappe.new_doc("Footer Component")
    doc_footer_comp = get_mapped_doc("Footer Component", name,	{
        "Footer Component": {
            "doctype": "Footer Component"
        },
    }, target_doc, ignore_permissions=True)
    doc_footer_comp.idx = None
    doc_footer_comp.web_section = []
    doc_footer_comp.title = doc_footer_comp.title + ' ' + sub_name

    web_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": name, "parentfield": "web_section"}, fields=[
        'section', 'section_title', 'section_type', 'content_type', 'allow_update_to_style', 'idx', 'column_index'], order_by="idx")
    web_secs = []
    for x in web_sections:
        target_doc = None
        doc = frappe.new_doc("Page Section")
        doc = get_mapped_doc("Page Section", x.section,	{
            "Page Section": {
                "doctype": "Page Section"
            },
        }, target_doc, ignore_permissions=True)
        if doc.section_type == 'Menu':
            target_doc = None
            doc_menu = frappe.new_doc("Menu")
            doc_menu = get_mapped_doc("Menu", doc.menu,	{
                "Menu": {
                    "doctype": "Menu"
                },
            }, target_doc, ignore_permissions=True)
            # doc_menu.title = doc_menu.title + ' ' + sub_name
            doc_menu.id_parent_copy = doc.menu
            doc_menu.title = doc_menu.title
            doc_menu.id_client_website = sub_name
            doc_menu.save(ignore_permissions=True)
            doc.menu = doc_menu.name
        doc.save(ignore_permissions=True)

        m_page_sec = frappe.new_doc("Mobile Page Section")
        m_page_sec.section_title = x.section_title
        m_page_sec.section_type = x.section_type
        m_page_sec.content_type = x.content_type
        m_page_sec.allow_update_to_style = x.allow_update_to_style
        m_page_sec.idx = x.idx
        m_page_sec.column_index = x.column_index
        m_page_sec.parentfield = "web_section"
        m_page_sec.parenttype = "Footer Component"
        m_page_sec.section = doc.name
        web_secs.append(m_page_sec)

    doc_footer_comp.web_section = web_secs
    doc_footer_comp.save(ignore_permissions=True)
    # frappe.db.commit()
    return doc_footer_comp.name


def copy_web_theme(name, sub_name, cp_header, cp_footer):
    target_doc = None
    web_theme = frappe.new_doc("Web Theme")
    web_theme = get_mapped_doc("Web Theme", name,	{
        "Web Theme": {
            "doctype": "Web Theme"
        },
    }, target_doc, ignore_permissions=True)
    web_theme.name = name + ' ' + sub_name
    web_theme.default_header = cp_header
    web_theme.default_footer = cp_footer
    web_theme.is_active = 0
    web_theme.container_width = ''
    web_theme.save(ignore_permissions=True)
    # frappe.db.commit()
    return web_theme.name


def get_section_content(section, content_type):
    section = frappe.db.get_all('Page Section', filters={'name': section}, fields=[
        'section_name', 'section_type', 'name', 'reference_document', 'fetch_product', 'reference_name', 'no_of_records', 'image',
        'custom_section_data', 'display_data_randomly', 'dynamic_data', 'menu', 'html_content', 'section_title'
    ])

    if section:
        section[0].fields = frappe.db.sql('''select field_label, field_key, field_type, content, name, group_name, fields_json,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and parenttype = "Page Section" order by idx''', {
            'parent': section[0].name, 'content_type': content_type}, as_dict=1)
    return section[0]


def get_field_section_component(web_edit, web_section):
    fields_st_cp = []
    for item in web_section:
        info_item = get_section_content(item.section, 'Data')
        if item.section_name in ['Header Logo', 'Header Button']:
            info_item['allow_edit'] = False
            info_item['show_edit'] = False
        else:
            info_item['allow_edit'] = True
            info_item['show_edit'] = True
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
                    'show_edit': True,
                    'doctype': "Menu",
                    'filters': {
                        'id_client_website': web_edit.name
                    }

                }
            ]
        if info_item.get('section_type') == "Html Content":
            info_item['fields_ps'] = [
                {
                    'field_label': 'Nội dung trang',
                    'field_key': 'html_content',
                    'field_type': 'texeditor',
                    'content': info_item.get('html_content'),
                    'allow_edit': True,
                    'show_edit': True,
                }
            ]

        for field in info_item['fields']:
            field['allow_edit'] = True
            field['show_edit'] = True
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

    return fields_st_cp


def update_fields_page_section(data):
    if data.get('fields_st_cp') and type(data.get('fields_st_cp')) == list:
        for fcp in data.get('fields_st_cp'):
            if fcp.get("show_edit") and fcp.get("allow_edit") and fcp.get('fields'):
                for field in fcp.get('fields'):
                    if field.get('group_name'):
                        for f in field.get('fields'):
                            if f.get("show_edit") and f.get("allow_edit"):
                                # update Section Content
                                content = f.get('content')
                                if f.get('field_type') in FIELD_TYPE_JSON:
                                    content = json.dumps(f.get('content'))
                                frappe.db.set_value('Section Content', f.get('name'), {
                                    'content': content
                                })
                    else:
                        if field.get("show_edit") and field.get("allow_edit"):
                            # update Section Content
                            content = field.get('content')
                            if field.get('field_type') in FIELD_TYPE_JSON:
                                content = json.dumps(field.get('content'))
                            frappe.db.set_value('Section Content', field.get('name'), {
                                'content': content
                            })

            if fcp.get("show_edit") and fcp.get("allow_edit") and fcp.get("fields_ps"):
                d_update = {}
                update_ps = False
                for field in fcp.get('fields_ps'):
                    if field.get('field_type') == "texeditor" and field.get('field_key') == "html_content":
                        update_ps = True
                    d_update[field.get('field_key')] = field.get(
                        'content')
                if d_update:
                    frappe.db.set_value(
                        'Page Section', fcp.get('name'), d_update)
                if update_ps:
                    ps = frappe.get_doc('Page Section', fcp.get('name'))
                    ps.save()


def update_fields_page(data):
    data_update = {}
    if data.get('fields_cp') and type(data.get('fields_cp')) == list:
        for field_cp in data.get('fields_cp'):
            if field_cp.get("show_edit") and field_cp.get('allow_edit') and field_cp.get('fields'):
                for field in field_cp.get('fields'):
                    if field.get('group_name'):
                        for f in field.get('fields'):
                            if f.get("show_edit") and f.get("allow_edit"):
                                data_update[f.get('field_key')] = f.get(
                                    'content')
                    else:
                        if field.get("show_edit") and field.get("allow_edit"):
                            data_update[field.get('field_key')] = field.get(
                                'content')
    return data_update
