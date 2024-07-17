from slugify import slugify
import os
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
import json
import time

FIELD_TYPE_JSON = ["List", 'Button']


def getStrTimestamp():
    arr_time = str(time.time()).split('.')
    while (len(arr_time[1]) < 7):
        arr_time[1] += '0'

    return arr_time[0] + arr_time[1]


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
    doc_header_comp.is_template = 0
    doc_header_comp.title = "US-H-{0}-{1}".format(
        doc_header_comp.title, getStrTimestamp())

    web_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": name, "parentfield": "web_section", "parenttype": "Header Component"}, fields=[
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
            doc_menu.name = "US-M-{0}".format(getStrTimestamp())
            doc_menu.id_parent_copy = doc.menu
            doc_menu.title = doc_menu.title
            doc_menu.id_client_website = sub_name
            doc_menu.is_template = 0
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
    doc_footer_comp.is_template = 0
    doc_footer_comp.title = "US-H-{0}-{1}".format(
        doc_footer_comp.title, getStrTimestamp())

    web_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": name, "parentfield": "web_section", "parenttype": "Footer Component"}, fields=[
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
            doc_menu.name = "US-M-{0}".format(getStrTimestamp())
            doc_menu.id_parent_copy = doc.menu
            doc_menu.title = doc_menu.title
            doc_menu.id_client_website = sub_name
            doc_menu.is_template = 0
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
    web_theme.name = "US-WT-{0}-{1}".format(name, getStrTimestamp())
    web_theme.default_header = cp_header
    web_theme.default_footer = cp_footer
    web_theme.is_active = 0
    web_theme.is_template = 0
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
                        'id_client_website': web_edit.name,
                        'is_template': 0,
                    }

                }
            ]
        if info_item.get('section_type') == "Html Content":
            info_item['fields_ps'] = [
                {
                    'field_label': 'Nội dung trang',
                    'field_key': 'html_content',
                    'field_type': 'texteditor',
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
                    if field.get('field_type') == "texteditor" and field.get('field_key') == "html_content":
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


def v(i):
    import datetime
    if isinstance(i, (datetime.datetime, datetime.date, datetime.time)):
        return str(i)
    return i


def remove_nulls(d):
    if isinstance(d, dict):
        return {k: remove_nulls(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_nulls(item) for item in d]
    else:
        return d


def write_page_section(parent, path, parenttype):
    web_sections = frappe.db.get_all("Mobile Page Section", filters={
                                     "parent": parent, "parentfield": "web_section", "parenttype": parenttype}, fields=['section', 'column_index', 'idx'], order_by="idx")

    page_sections = []
    for sec in web_sections:
        doc = frappe.get_doc('Page Section', sec.section).as_dict()
        doc['idx'] = sec.idx
        doc['column_index'] = sec.column_index
        # remove fields is None
        doc = remove_nulls(doc)
        page_sections.append(doc)

    # check folder not exists then create folder
    if not os.path.exists(path):
        os.mkdir(path)
    # write file
    json_file_name = "section.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump(page_sections, f, ensure_ascii=False, default=v)


def write_file_page_template(name, version='page_template_v1'):
    folder_name = slugify(text=name, separator='_')
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'mbw_json_data', version, folder_name)

    page_temp = frappe.get_doc('Page Template', name).as_dict()
    page_temp['web_section'] = []
    page_temp['mobile_section'] = []
    # remove fields is None
    page_temp = remove_nulls(page_temp)

    # check folder not exists then create folder
    if not os.path.exists(path):
        os.mkdir(path)
    # write file
    json_file_name = "page_template.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump([page_temp], f, ensure_ascii=False, default=v)

    # sections
    write_page_section(name, path, "Page Template")


def write_file_header_component(name, version='header_component_v1'):
    folder_name = slugify(text=name, separator='_')
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'mbw_json_data', version, folder_name)

    header_comp = frappe.get_doc('Header Component', name).as_dict()
    header_comp['web_section'] = []
    # remove fields is None
    header_comp = remove_nulls(header_comp)

    # check folder not exists then create folder
    if not os.path.exists(path):
        os.mkdir(path)
    # write file
    json_file_name = "page_template.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump([header_comp], f, ensure_ascii=False, default=v)

    # sections
    write_page_section(name, path, 'Header Component')


def write_file_footer_component(name, version='footer_component_v1'):
    folder_name = slugify(text=name, separator='_')
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'mbw_json_data', version, folder_name)

    footer_comp = frappe.get_doc('Footer Component', name).as_dict()
    footer_comp['web_section'] = []
    # remove fields is None
    footer_comp = remove_nulls(footer_comp)

    # check folder not exists then create folder
    if not os.path.exists(path):
        os.mkdir(path)
    # write file
    json_file_name = "page_template.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump([footer_comp], f, ensure_ascii=False, default=v)

    # sections
    write_page_section(name, path, 'Footer Component')


def create_file_template():
    print('==========================create_file_template===========================')

    # header
    header_comps = frappe.db.get_all(
        'Header Component', {'is_template': 1}, pluck="name")
    for h in header_comps:
        print('Header Component', h)
        write_file_header_component(h)
    # footer
    header_comps = frappe.db.get_all(
        'Footer Component', {'is_template': 1}, pluck="name")
    for f in header_comps:
        print('Footer Component', f)
        write_file_footer_component(f)

    # page template
    page_temps = frappe.db.get_all('Page Template',  pluck="name")
    for p in page_temps:
        print('Page Template', p)
        write_file_page_template(p)
    print('=========================Done create_file_template============================')


def handle_write_file_multiple_doctype_template():
    print('=======================handle_write_file_multiple_doctype_template=======================')
    doctypes = ['Color Palette', 'Header Layout', 'Footer Layout', 'Section Template Group', 'Section Template',
                'CMS Settings', 'Menu', 'MBW Form', 'Web Theme', 'MBW Website Template', 'Blogger']
    temps = []
    for d in doctypes:
        if d not in ['CMS Settings']:
            filters = []
            if d in ["Menu", "Web Theme", "MBW Form"]:
                filters = [['is_template', '=', 1]]

            temps.append({
                "doc_names": frappe.db.get_all(d, filters, pluck="name"),
                "doctype": d
            })
        else:
            temps.append({
                "doc_names": [d],
                "doctype": d
            })

    for temp in temps:
        data = []
        for doc in temp.get('doc_names'):
            print(temp.get('doctype'), doc)
            d_j = frappe.get_doc(temp.get('doctype'), doc).as_dict()
            # remove fields is None
            d_j = remove_nulls(d_j)
            data.append(d_j)

        # write file
        path = os.path.join(frappe.get_module_path("go1_cms"), 'mbw_json_data')
        folder_name = slugify(text=temp.get('doctype'), separator='_')
        json_file_name = "{0}.json".format(folder_name)
        with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=v)
    print('=======================DONE handle_write_file_multiple_doctype_template=======================')


def get_all_folder_in_dir(version):
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'mbw_json_data', version)
    return os.listdir(path)
