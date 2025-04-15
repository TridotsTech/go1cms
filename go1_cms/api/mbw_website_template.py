import frappe
from frappe import _
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
from go1_cms.api.wrapper_api import (
    check_user_admin
)
from go1_cms.api.export_template import (
    install_template
)


@frappe.whitelist()
@check_user_admin
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
@check_user_admin
def get_web_template(name):
    if not frappe.db.exists('MBW Website Template', name):
        frappe.throw(_("Interface not found"), frappe.DoesNotExistError)
    template = frappe.get_doc('MBW Website Template', name).as_dict()
    published = 0
    web_client = frappe.db.exists(
        "MBW Client Website", {"setting_from_template": name})
    if web_client:
        published = frappe.db.get_value(
            'MBW Client Website', web_client, 'published')

    template.client_web = {
        'published': published
    }

    return template


@frappe.whitelist()
@check_user_admin
def create_client_website(name):
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

                new_webpage.append("mobile_section", mb_page_new.as_dict())
                # mobile_section.append(mb_page_new)

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

                new_webpage.append("web_section", mb_page_new.as_dict())
                # web_section.append(mb_page_new)

            # new_webpage.mobile_section = mobile_section
            # new_webpage.web_section = web_section
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
            item_cl_web.category = page_temp.category
            item_cl_web.idx = idx_p

            website.append("page_websites", item_cl_web.as_dict())
            # page_websites.append(item_cl_web)

        # copy web theme
        web_theme = None
        if template.web_theme:
            web_theme = copy_web_theme(
                template.web_theme, website.name, cp_header, cp_footer)

        # update client website
        website.name_web = template.template_name
        website.published = 1
        website.web_theme = web_theme
        website.edit = 1
        website.type_web = 'Bản chính'
        website.type_template = template.type_template
        website.header_component = cp_header
        website.footer_component = cp_footer
        # website.page_websites = page_websites
        website.setting_from_template = name
        website.save(ignore_permissions=True)

        # update edit website
        update_edit_client_website(website.name)

        # update web template
        template.template_in_use = 1
        template.installed_template = 1
        template.save(ignore_permissions=True)

        return {'name': website.name, 'template_edit': None}
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except frappe.DoesNotExistError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex), frappe.DoesNotExistError)
    except Exception as ex:
        frappe.throw(_("An error has occurred"))


@frappe.whitelist()
@check_user_admin
def prepare_file_template(name):
    # return {'code': 200, 'msg': _("Interface loaded successfully")}
    rs = install_template(name)
    if rs:
        return {'code': 200, 'msg': _("Interface loaded successfully")}
    else:
        return {'code': 0, 'msg': _("Failed to load interface")}
