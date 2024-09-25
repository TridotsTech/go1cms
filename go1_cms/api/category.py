import frappe
from frappe import _
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_category(name):
    MbwBlogCategory = frappe.qb.DocType("Mbw Blog Category")
    query = (
        frappe.qb.from_(MbwBlogCategory)
        .select("*")
        .where(MbwBlogCategory.name == name)
    ).limit(1)

    category = query.run(as_dict=True)
    if not len(category):
        frappe.throw(_("Category not found"), frappe.DoesNotExistError)
    category = category.pop()
    return category


@frappe.whitelist()
@check_user_admin
def create_category(data):
    category_title = data.get('category_title')
    if not category_title:
        frappe.throw(_("Tên danh mục không được để trống"))
    if frappe.db.exists("Mbw Blog Category", {"category_title": category_title}):
        frappe.throw(_("Tên danh mục đã tồn tại"))

    doc_new = frappe.new_doc('Mbw Blog Category')
    doc_new.category_title = category_title
    doc_new.description = data.get('description')
    doc_new.insert()

    result = {'name': doc_new.name}
    return result


@frappe.whitelist()
@check_user_admin
def update_category(data):
    doc_name = data.get('name')
    category_title = data.get('category_title')
    if not frappe.db.exists("Mbw Blog Category", doc_name):
        frappe.throw(_("Category not found"), frappe.DoesNotExistError)

    if not category_title:
        frappe.throw(_("Tên danh mục không được để trống"))

    if frappe.db.exists("Mbw Blog Category", {"category_title": category_title, "name": ("!=", doc_name)}):
        frappe.throw(_("Tên danh mục đã tồn tại"))

    doc = frappe.get_doc('Mbw Blog Category', doc_name)
    if doc.name != category_title:
        frappe.rename_doc(doc.doctype, doc.name, category_title, merge=False)

    doc = frappe.get_doc('Mbw Blog Category', category_title)
    doc.category_title = category_title
    doc.description = data.get('description')
    doc.save()

    result = {'name': doc.name}
    return result


@frappe.whitelist()
@check_user_admin
def delete_category(name):
    try:
        if not frappe.db.exists("Mbw Blog Category", name):
            frappe.throw(_("Category not found"), frappe.DoesNotExistError)

        MbwBlogPost = frappe.qb.DocType("Mbw Blog Post")
        query = (
            frappe.qb.from_(MbwBlogPost)
            .select("name")
            .where(MbwBlogPost.blog_category == name)
        )
        blogs = query.run(as_dict=True)
        for blog in blogs:
            frappe.delete_doc('Mbw Blog Post', blog.name)

        frappe.delete_doc('Mbw Blog Category', name)

        result = {'name': name}
        return result
    except frappe.LinkExistsError as ex:
        frappe.clear_last_message()
        frappe.throw(_("Danh mục này đã được liên kết, không thể xóa."))
    except Exception as ex:
        frappe.throw(_(f"Lỗi: {str(ex)}"))
