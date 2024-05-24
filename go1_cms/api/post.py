import frappe
from frappe import _


@frappe.whitelist()
def get_post(name):
    MbwBlogPost = frappe.qb.DocType("Mbw Blog Post")
    query = (
        frappe.qb.from_(MbwBlogPost)
        .select("*")
        .where(MbwBlogPost.name == name)
    ).limit(1)

    post = query.run(as_dict=True)
    if not len(post):
        frappe.throw(_("Blog not found"), frappe.DoesNotExistError)
    post = post.pop()
    return post


@frappe.whitelist()
def create_post(data):
    if not data.get('title'):
        frappe.throw(_("Tên bài viết không được để trống"))

    if not data.get('blog_category'):
        frappe.throw(_("Danh mục không được để trống"))

    doc_new = frappe.new_doc('Mbw Blog Post')
    doc_new.title = data.get('title')
    doc_new.blog_intro = data.get('blog_intro')
    doc_new.meta_title = data.get('meta_title')
    doc_new.meta_description = data.get('meta_description')
    doc_new.meta_keywords = data.get('meta_keywords')
    doc_new.blog_category = data.get('blog_category')
    doc_new.content = data.get('content') or ''
    doc_new.route = data.get('route')
    doc_new.published = 1 if data.get(
        'published') and data.get('published') == True else 0
    doc_new.blogger = 'Admin'
    doc_new.insert()

    result = {'name': doc_new.name}
    return result


@frappe.whitelist()
def update_post(data):
    doc_name = data.get('name')
    if not frappe.db.exists("Mbw Blog Post", doc_name):
        frappe.throw(_("Blog not found"), frappe.DoesNotExistError)

    if not data.get('title'):
        frappe.throw(_("Tên bài viết không được để trống"))

    if not data.get('blog_category'):
        frappe.throw(_("Danh mục không được để trống"))

    doc = frappe.get_doc('Mbw Blog Post', doc_name)
    doc.title = data.get('title')
    doc.blog_intro = data.get('blog_intro')
    doc.meta_title = data.get('meta_title')
    doc.meta_description = data.get('meta_description')
    doc.meta_keywords = data.get('meta_keywords')
    doc.blog_category = data.get('blog_category')
    doc.meta_image = data.get('meta_image')
    doc.content = data.get('content') or ''
    doc.route = data.get('route')
    doc.published = 1 if data.get(
        'published') and data.get('published') == True else 0
    doc.save()

    result = {'name': doc.name}
    return result


@frappe.whitelist()
def delete_post(name):
    if not frappe.db.exists("Mbw Blog Post", name):
        frappe.throw(_("Post not found"), frappe.DoesNotExistError)

    frappe.delete_doc('Mbw Blog Post', name)

    result = {'name': name}
    return result
