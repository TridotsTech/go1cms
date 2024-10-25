import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_field_section_component,
    update_fields_page_section,
    update_fields_page,
    get_domain
)
from slugify import slugify
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_info_page(name):
    if not frappe.db.exists("MBW Client Website Item", name):
        frappe.throw(_("Không tìm thấy trang"), frappe.DoesNotExistError)
    web_item = frappe.db.get_value(
        'MBW Client Website Item', name, ['name', 'page_id', 'name_page', 'allow_delete', 'page_type', 'category'], as_dict=1)
    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name'], as_dict=1)
    web_page = frappe.get_doc('Web Page Builder', web_item.page_id)

    # get field section in component
    fields_st_cp = get_field_section_component(web_edit, web_page.web_section)

    # fields component
    fields_cp = []

    # get field group 0
    fields_page = {
        'allow_edit': web_item.page_type == "Trang chi tiết tin tức",
        'show_edit': web_item.page_type == "Trang chi tiết tin tức",
        'section_title': 'Áp dụng trang cho bài viết',
        'show_prv_image': False,
        'fields': [
            {
                'field_label': 'Thuộc danh mục',
                'field_key': 'category',
                'field_type': 'Link',
                'content': web_item.category,
                'allow_edit': web_item.page_type == "Trang chi tiết tin tức",
                'show_edit': web_item.page_type == "Trang chi tiết tin tức",
                'doctype': "Mbw Blog Category",
                'filters': {}
            },
        ],
        'name': 'group-0'
    }
    fields_cp.append(fields_page)

    # get field group 1
    domain = get_domain()

    fields_page = {
        'allow_edit':  web_item.page_type == "",
        'show_edit': web_item.page_type == "",
        'section_title': 'Chuyển hướng',
        'show_prv_image': False,
        'fields': [
            {
                'field_label': 'Link chuyển hướng',
                'field_key': 'route_template',
                'field_type': 'Data',
                'content': web_page.route,
                'allow_edit': web_item.allow_delete,
                'show_edit': True,
                'description': web_page.route,
                'label_des': f'<strong>{domain}/</strong>',
            },
            {
                'field_label': 'Route Default',
                'field_key': 'route_default',
                'field_type': 'Data',
                'content': web_page.route,
                'allow_edit': False,
                'show_edit': False
            },
        ],
        'name': 'group-1'
    }
    fields_cp.append(fields_page)

    # get field group seo
    fields_page = {
        'allow_edit':  True,
        'show_edit': True,
        'section_title': 'SEO',
        'show_prv_image': False,
        'fields': [
            {
                'field_label': 'Thẻ tiêu đề',
                'field_key': 'meta_title',
                'field_type': 'Data',
                'content': web_page.meta_title,
                'allow_edit': True,
                'show_edit': True,
            },
            {
                'group_name': 'seo-1',
                'section_title': '',
                'show_edit': True,
                'fields': [
                    {
                        'field_label': 'Thẻ mô tả',
                        'field_key': 'meta_description',
                        'field_type': 'Small Text',
                        'content': web_page.meta_description,
                        'allow_edit': True,
                        'show_edit': True,
                    },
                    {
                        'field_label': 'Thẻ từ khóa',
                        'field_key': 'meta_keywords',
                        'field_type': 'Small Text',
                        'content': web_page.meta_keywords,
                        'allow_edit': True,
                        'show_edit': True,
                    },
                ]
            },
        ],
        'name': 'group-2'
    }
    fields_cp.append(fields_page)

    web_page_info = {
        'is_detail_page': True if web_item.page_type else False,
        'web_item': name,
        'name_page': web_item.name_page,
        'doc_page': web_item.page_id,
        'allow_delete': web_item.allow_delete == 1,
        'route': '/' + web_page.route
    }
    return {'fields_cp': fields_cp, 'fields_st_cp': fields_st_cp, 'web_page': web_page_info}


@frappe.whitelist()
@check_user_admin
def update_info_page(data):
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

        category = data_update.pop("category", None)
        route_template = data_update.get('route_template')
        if route_template:
            ls_route = [slugify(i) for i in route_template.split('/')]
            route_template = '/'.join([i for i in ls_route if i])
            data_update['route_template'] = route_template

        if not route_template:
            data_update.pop("route_template", None)

        if data_update:
            frappe.db.set_value('Web Page Builder',
                                web_page.name, data_update)
        # update web item
        web_item = data.get('web_page').get('web_item')
        if frappe.db.exists("MBW Client Website Item", web_item):
            frappe.db.set_value('MBW Client Website Item', web_item, {
                'category': category
            })

        web_page.reload()
        web_page.save()

        return {'name': web_page.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Có lỗi xảy ra')


@frappe.whitelist()
@check_user_admin
def delete_page(name):
    try:
        web_item = frappe.db.get_value('MBW Client Website Item', name, [
                                       'page_id', 'allow_delete'], as_dict=1)
        if not web_item:
            frappe.throw(_("Không tìm thấy trang xóa"),
                         frappe.DoesNotExistError)
        if web_item.allow_delete == 0:
            frappe.throw(_("Trang không thể xóa"),
                         frappe.DoesNotExistError)

        # delete MBW Client Website Item
        frappe.delete_doc('MBW Client Website Item', name)
        # delete Web Page Builder
        frappe.delete_doc('Web Page Builder', web_item.page_id)
    except Exception as ex:
        print(ex)
        frappe.throw('Có lỗi xảy ra')
