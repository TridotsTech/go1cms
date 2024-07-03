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
    # category
    category = frappe.db.get_all("Mbw Blog Category Item", filters={"parent": name, "parentfield": "category"}, fields=[
        'name', 'category', 'idx'
    ], order_by="idx")
    post['category'] = category
    # tags
    tags = frappe.db.get_all("MBW Blog Tag Item", filters={"parent": name, "parentfield": "tags"}, fields=[
        'name', 'tag', 'idx'
    ], order_by="idx")
    post['tags'] = tags
    return post


@frappe.whitelist()
def create_post(data):
    if not data.get('title'):
        frappe.throw(_("Tên bài viết không được để trống"))

    doc_new = frappe.new_doc('Mbw Blog Post')
    doc_new.title = data.get('title')
    doc_new.blog_intro = data.get('blog_intro')
    doc_new.meta_title = data.get('meta_title')
    doc_new.meta_description = data.get('meta_description')
    doc_new.meta_keywords = data.get('meta_keywords')
    # add category
    category = []
    for cat in data.get('category', []):
        if frappe.db.exists({"doctype": "Mbw Blog Category", "name": cat.get('name')}):
            new_cat = frappe.new_doc("Mbw Blog Category Item")
            new_cat.category = cat.get('name')
            category.append(new_cat)
    doc_new.category = category
    # add tags
    tags = []
    for tag in data.get('tags', []):
        if frappe.db.exists({"doctype": "MBW Blog Tag", "name": tag.get('name')}):
            new_tag = frappe.new_doc("MBW Blog Tag Item")
            new_tag.tag = tag.get('name')
            tags.append(new_tag)
    doc_new.tags = tags

    doc_new.blog_tag = data.get('blog_tag')
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

    doc = frappe.get_doc('Mbw Blog Post', doc_name)
    # remove category not in list
    for cat in doc.category:
        if not next((item for item in data.get('category', []) if item.get('name') == cat.category), None):
            frappe.delete_doc('Mbw Blog Category Item', cat.name)
    # remove tags not in list
    for tag in doc.tags:
        if not next((item for item in data.get('tags', []) if item.get('name') == tag.tag), None):
            frappe.delete_doc('MBW Blog Tag Item', tag.name)

    doc.reload()
    # add new category
    category = doc.category
    idx = 1
    for cat in data.get('category', []):
        category_exs = next(
            (item for item in category if cat.get('name') == item.category), None)
        if not category_exs:
            if frappe.db.exists({"doctype": "Mbw Blog Category", "name": cat.get('name')}):
                new_cat = frappe.new_doc("Mbw Blog Category Item")
                new_cat.category = cat.get('name')
                new_cat.idx = len(category) + 1
                category.append(new_cat)
        else:
            category_exs.idx = idx
        idx += 1

    # add new tag
    tags = doc.tags
    idx = 1
    for tag in data.get('tags', []):
        tag_exs = next(
            (item for item in tags if tag.get('name') == item.tag), None)
        if not tag_exs:
            if frappe.db.exists({"doctype": "MBW Blog Tag", "name": tag.get('name')}):
                new_tag = frappe.new_doc("MBW Blog Tag Item")
                new_tag.tag = tag.get('name')
                new_tag.idx = idx
                tags.append(new_tag)
        else:
            tag_exs.idx = idx
        idx += 1

    doc.title = data.get('title')
    doc.blog_intro = data.get('blog_intro')
    doc.meta_title = data.get('meta_title')
    doc.meta_description = data.get('meta_description')
    doc.meta_keywords = data.get('meta_keywords')
    doc.blog_tag = data.get('blog_tag')
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
