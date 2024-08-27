import frappe
from frappe import _
from pypika import Criterion
from go1_cms.go1_cms.doctype.web_page_builder.web_page_builder import import_sections_from_template
from go1_cms.api.common import (
    copy_header_component,
    copy_footer_component,
    copy_web_theme
)
from slugify import slugify
from go1_cms.api.client_website import (
    update_edit_client_website
)


@frappe.whitelist()
def get_web_templates(repo):
    WebTemplate = frappe.qb.DocType("MBW Website Template")
    query = (
        frappe.qb.from_(WebTemplate)
        .select("*")
    )

    if repo != 'all':
        query = query.where(WebTemplate.type_template == repo)

    templates = query.run(as_dict=True)
    return templates


@frappe.whitelist()
def get_web_template(name):
    WebTemplate = frappe.qb.DocType("MBW Website Template")
    if not frappe.db.exists('MBW Website Template', name):
        frappe.throw(_("Template not found"), frappe.DoesNotExistError)
    template = frappe.get_doc('MBW Website Template', name)

    return template


@frappe.whitelist()
def add_web_template(name):
    try:
        template = frappe.get_doc("MBW Website Template", name)
        if not template:
            frappe.throw(_("Template not found"), frappe.DoesNotExistError)

        website = frappe.new_doc("MBW Client Website")
        website.name_web = "New"
        website.save(ignore_permissions=True)
        website.reload()

        page_websites = []
        cp_header = None
        cp_footer = None
        idx_p = 0
        for page_temp in template.page_templates:
            idx_p += 1
            new_webpage = frappe.new_doc("Web Page Builder")
            new_import = import_sections_from_template(
                page_id=page_temp.page_template, id_client_website=website.name)

            page_build_name = slugify(page_temp.name_template) + \
                ' ' + frappe.scrub(website.name)

            info = new_import.get('info')
            mobile_sections = new_import.get('mobile_sections')
            web_sections = new_import.get('web_sections')

            new_webpage.page_title = page_build_name
            new_webpage.web_client_id = website.name
            new_webpage.published = info.published
            new_webpage.page_type = info.page_type
            new_webpage.meta_title = info.meta_title
            new_webpage.meta_keywords = info.meta_keywords
            new_webpage.meta_description = info.meta_description
            new_webpage.use_page_builder = info.use_page_builder
            new_webpage.is_location_based = 0
            if info.content:
                new_webpage.content = info.content
            if info.header_component:
                if not cp_header:
                    cp_header = copy_header_component(
                        info.header_component, website.name)
                new_webpage.header_component = cp_header
            if info.footer_component:
                if not cp_footer:
                    cp_footer = copy_footer_component(
                        info.footer_component, website.name)
                new_webpage.footer_component = cp_footer

            mobile_section = []
            idx = 0
            for mb_st in mobile_sections:
                idx += 1
                mb_page_new = frappe.new_doc('Mobile Page Section')
                mb_page_new.allow_update_to_style = mb_st.allow_update_to_style
                mb_page_new.content_type = mb_st.content_type
                mb_page_new.section = mb_st.section
                mb_page_new.section_title = mb_st.section_title
                mb_page_new.section_type = mb_st.section_type
                mb_page_new.idx = idx
                mobile_section.append(mb_page_new)

            web_section = []
            idx = 0
            for wb_st in web_sections:
                idx += 1
                mb_page_new = frappe.new_doc('Mobile Page Section')
                mb_page_new.allow_update_to_style = wb_st.allow_update_to_style
                mb_page_new.content_type = wb_st.content_type
                mb_page_new.section = wb_st.section
                mb_page_new.section_title = wb_st.section_title
                mb_page_new.section_type = wb_st.section_type
                mb_page_new.idx = idx
                web_section.append(mb_page_new)

            new_webpage.mobile_section = mobile_section
            new_webpage.web_section = web_section
            new_webpage.save(ignore_permissions=True)

            # add item client web
            item_cl_web = frappe.new_doc("MBW Client Website Item")
            item_cl_web.page_id = page_build_name
            item_cl_web.allow_edit = page_temp.allow_edit
            item_cl_web.allow_delete = page_temp.allow_delete
            item_cl_web.name_page = page_temp.name_template
            item_cl_web.icon = page_temp.icon
            item_cl_web.route_template = page_temp.route_template
            item_cl_web.page_type = page_temp.page_type
            item_cl_web.idx = idx_p
            page_websites.append(item_cl_web)

        # copy web theme
        web_theme = None
        if template.web_theme:
            web_theme = copy_web_theme(
                template.web_theme, website.name, cp_header, cp_footer)

        # update client website
        # check template edit
        # template_edit = frappe.db.exists('MBW Client Website', {'edit': 1})
        # website.edit = 0 if template_edit else 1

        website.name_web = template.template_name
        website.published = 1
        website.web_theme = web_theme
        website.edit = 0
        website.type_web = 'Bản chính'
        website.type_template = template.type_template
        website.header_component = cp_header
        website.footer_component = cp_footer
        website.page_websites = page_websites
        website.save(ignore_permissions=True)

        # update edit website
        update_edit_client_website(website.name)

        return {'name': website.name, 'template_edit': None}
    except Exception as ex:
        frappe.throw(_("Lỗi hệ thống"))
