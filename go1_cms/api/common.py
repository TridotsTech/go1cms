import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc


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
            doc_menu.title = doc_menu.title
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
            doc_menu.title = doc_menu.title
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


def get_section_content(section, content_type):
    section = frappe.db.get_all('Page Section', filters={'name': section}, fields=[
        'section_type', 'name', 'reference_document', 'fetch_product', 'reference_name', 'no_of_records',
        'custom_section_data', 'display_data_randomly', 'dynamic_data', 'menu', 'section_title'
    ])

    if section:
        section[0].fields = frappe.db.sql('''select field_label, field_key, field_type, content, name, group_name, fields_json,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and parenttype = "Page Section" order by idx''', {
            'parent': section[0].name, 'content_type': content_type}, as_dict=1)
    return section[0]
