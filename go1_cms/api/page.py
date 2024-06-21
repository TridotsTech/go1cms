import frappe
from frappe import _
import json
from go1_cms.api.common import (
    get_field_section_component,
    update_fields_page_section,
    update_fields_page
)


@frappe.whitelist()
def get_info_page(name):
    web_item = frappe.get_doc('MBW Client Website Item', name)
    if not web_item:
        frappe.throw(_("Page not found"), frappe.DoesNotExistError)
    web_edit = frappe.db.get_value(
        'MBW Client Website', {"edit": 1}, ['name'], as_dict=1)
    web_page = frappe.get_doc('Web Page Builder', web_item.page_id)

    # get field section in component
    fields_st_cp = get_field_section_component(web_edit, web_page.web_section)

    # fields component
    fields_cp = []
    # get field group 1
    fields_page = {
        'allow_edit':  False,
        'show_edit': True,
        'section_title': 'Chuyển hướng',
        'show_prv_image': False,
        'fields': [
            {
                'field_label': 'Link chuyển hướng',
                'field_key': 'route',
                'field_type': 'Data',
                'content': '/' + web_page.route,
                'allow_edit': False,
                'show_edit': True,
            }
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
        'name': 'group-1'
    }
    fields_cp.append(fields_page)

    web_page_info = {
        'name_page': web_item.name_page,
        'doc_page': web_item.page_id,
        'allow_delete': web_item.allow_delete == 1
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
        data_update = {}
        update_fields_page(data, data_update)

        if data_update:
            frappe.db.set_value('Web Page Builder',
                                web_page.name, data_update)

        web_page.reload()
        web_page.save()

        return {'name': web_page.name}
    except Exception as ex:
        print("ex::", ex)
        frappe.throw('Lỗi hệ thống')


@frappe.whitelist()
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
        frappe.throw('Lỗi hệ thống')
