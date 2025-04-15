import frappe
from frappe import _
import json
from go1_cms.go1_cms.doctype.web_page_builder.web_page_builder import import_sections_from_template
from go1_cms.api.common import (
    get_field_section_component,
    update_fields_page_section,
    update_fields_page
)
from slugify import slugify
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_info_template_page():
    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name', 'type_web'], as_dict=1)
    web_item = frappe.db.get_value('MBW Client Website Item', {
        "parent": web_edit.name, "parentfield": "page_websites", 'page_type': 'Trang mới'}, ['page_id', 'name_page'], as_dict=1
    )
    if not web_item:
        return {}

    web_page = frappe.get_doc('Web Page Builder', web_item.page_id)

    # get field section in component
    fields_st_cp = get_field_section_component(web_edit, web_page.web_section)

    # fields component
    fields_cp = []
    # get field group button 1
    fields_page = {
        'allow_edit':  True,
        'show_edit': True,
        'section_title': 'SEO',
        'show_prv_image': False,
        'fields': [
            {
                'field_label': 'Meta title',
                'field_key': 'meta_title',
                'field_type': 'Data',
                'content': web_page.meta_title,
                'allow_edit': True,
                'show_edit': True,
                'upload_file_image': None
            },
            {
                'group_name': 'seo-1',
                'allow_edit': True,
                'show_edit': True,
                'fields': [
                    {
                        'field_label': 'Meta description',
                        'field_key': 'meta_description',
                        'field_type': 'Small Text',
                        'content': web_page.meta_description,
                        'allow_edit': True,
                        'show_edit': True,
                        'upload_file_image': None
                    },
                    {
                        'field_label': 'Meta keywords',
                        'field_key': 'meta_keywords',
                        'field_type': 'Small Text',
                        'content': web_page.meta_keywords,
                        'allow_edit': True,
                        'show_edit': True,
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
        'doc_page': web_item.page_id,
        'route_prefix': frappe.utils.get_url() + (f'/template_{web_edit.name}/' if web_edit.type_web == 'Bản nháp' else '/')
    }
    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'web_page': web_page_info}


@frappe.whitelist()
@check_user_admin
def update_info_template_page(data):
    try:
        page_id = None
        if data.get('web_page') and data.get('web_page').get('doc_page'):
            page_id = data.get('web_page').get('doc_page')
        if not page_id:
            frappe.throw(_("Page not found"),
                         frappe.DoesNotExistError)

        web_edit = frappe.db.exists("MBW Client Website", {"edit": 1})
        web_page = frappe.get_doc('Web Page Builder', page_id)

        if not web_edit or not web_page:
            frappe.throw(_("Page not found"),
                         frappe.DoesNotExistError)

        # update field section page
        update_fields_page_section(data)

        # reload page
        web_page.reload()

        # update field page
        data_update = update_fields_page(data)

        if data_update:
            frappe.db.set_value('Web Page Builder',
                                web_page.name, data_update)

        web_page.reload()
        web_page.save()

        return {'name': web_page.name}
    except Exception as ex:
        frappe.throw(_('An error has occurred'))


@frappe.whitelist()
@check_user_admin
def create_new_page(**kwargs):
    if not kwargs.get('name'):
        frappe.throw(_("Template page does not exist"))
    if not kwargs.get('name_page'):
        frappe.throw(_('Website name' + ' ' + _('cannot be empty')))

    if kwargs.get('route_page') and kwargs.get('route_page').strip():
        route_page = slugify(kwargs.get('route_page'))
    else:
        route_page = slugify(kwargs.get('name_page'))

    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name', 'type_web'], as_dict=1)
    # create
    new_webpage = frappe.new_doc("Web Page Builder")
    new_import = import_sections_from_template(
        kwargs.get('name'), "Web Page Builder", web_edit.name)

    client_web_item = frappe.get_last_doc(
        'MBW Client Website Item', filters={"parent": web_edit.name, "parentfield": "page_websites"})
    index_new_page = (client_web_item.index_new_page or 0) + 1
    page_build_name = slugify(kwargs.get('name_page')) + \
        ' ' + frappe.scrub(web_edit.name) + ' ' + str(index_new_page)

    info = new_import.get('info')
    mobile_sections = new_import.get('mobile_sections')
    web_sections = new_import.get('web_sections')

    new_webpage.page_title = page_build_name
    new_webpage.web_client_id = web_edit.name
    new_webpage.published = 1
    new_webpage.page_type = info.page_type
    new_webpage.meta_title = info.meta_title
    new_webpage.meta_keywords = info.meta_keywords
    new_webpage.meta_description = info.meta_description
    new_webpage.use_page_builder = info.use_page_builder
    new_webpage.is_location_based = 0
    if info.content:
        new_webpage.content = info.content
    new_webpage.header_component = info.header_component
    new_webpage.footer_component = info.footer_component

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

    if web_edit.type_web == 'Bản nháp':
        route_template = f'template_{web_edit.name}/' + route_page
        route_prefix = f'/template_{web_edit.name}'
    else:
        route_template = route_page
        route_prefix = ''
    # new_webpage.mobile_section = mobile_section
    # new_webpage.web_section = web_section
    new_webpage.route_template = route_template
    new_webpage.route_prefix = route_prefix
    new_webpage.save(ignore_permissions=True)

    # add item client web
    item_cl_web = frappe.new_doc("MBW Client Website Item")
    item_cl_web.parent = web_edit.name
    item_cl_web.parentfield = "page_websites"
    item_cl_web.parenttype = "MBW Client Website"
    item_cl_web.page_id = page_build_name
    item_cl_web.allow_edit = 1
    item_cl_web.allow_delete = 1
    item_cl_web.index_new_page = index_new_page
    item_cl_web.name_page = kwargs.get('name_page')
    item_cl_web.icon = 'WebpageIcon'
    item_cl_web.route_template = route_page
    item_cl_web.page_type = ''
    item_cl_web.idx = frappe.db.count('MBW Client Website Item', {
                                      "parent": web_edit.name, "parentfield": "page_websites"}) + 1
    item_cl_web.insert()

    return {'name': item_cl_web.name}
