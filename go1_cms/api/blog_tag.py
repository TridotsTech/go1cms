import frappe
from frappe import _
from go1_cms.api.wrapper_api import (
    check_user_admin
)


@frappe.whitelist()
@check_user_admin
def get_blog_tag(name):
    MBWBlogTag = frappe.qb.DocType("MBW Blog Tag")
    query = (
        frappe.qb.from_(MBWBlogTag)
        .select("*")
        .where(MBWBlogTag.name == name)
    ).limit(1)

    tags = query.run(as_dict=True)
    if not len(tags):
        frappe.throw(_("Tag not found"), frappe.DoesNotExistError)
    tags = tags.pop()
    return tags


@frappe.whitelist()
@check_user_admin
def create_blog_tag(data):
    title = data.get('title')
    if not title:
        frappe.throw(_("Tag name") + ' ' + _("cannot be empty"))
    if frappe.db.exists("MBW Blog Tag", {"title": title}):
        frappe.throw(_("Tag name already exists"))

    doc_new = frappe.new_doc('MBW Blog Tag')
    doc_new.title = title
    doc_new.description = data.get('description')
    doc_new.insert()

    result = {'name': doc_new.name}
    return result


@frappe.whitelist()
@check_user_admin
def update_blog_tag(data):
    doc_name = data.get('name')
    title = data.get('title')
    if not frappe.db.exists("MBW Blog Tag", doc_name):
        frappe.throw(_("Tag not found"), frappe.DoesNotExistError)

    if not title:
        frappe.throw(_("Tag name") + ' ' + _("cannot be empty"))

    if frappe.db.exists("MBW Blog Tag", {"title": title, "name": ("!=", doc_name)}):
        frappe.throw(_("Tag name already exists"))

    doc = frappe.get_doc('MBW Blog Tag', doc_name)
    if doc.name != title:
        frappe.rename_doc(doc.doctype, doc.name, title, merge=False)

    doc = frappe.get_doc('MBW Blog Tag', title)
    doc.title = title
    doc.description = data.get('description')
    doc.save()

    result = {'name': doc.name}
    return result


@frappe.whitelist()
@check_user_admin
def delete_blog_tag(name):
    try:
        if not frappe.db.exists("MBW Blog Tag", name):
            frappe.throw(_("Tag not found"), frappe.DoesNotExistError)

        if frappe.db.exists("MBW Blog Tag Item", {"tag": name}):
            frappe.throw(_("This tag is linked and cannot be deleted."))

        frappe.delete_doc('MBW Blog Tag', name)

        result = {'name': name}
        return result
    except frappe.LinkExistsError as ex:
        frappe.clear_last_message()
        frappe.throw(_("This tag is linked and cannot be deleted."))
    except frappe.ValidationError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex))
    except frappe.DoesNotExistError as ex:
        frappe.clear_last_message()
        frappe.throw(str(ex), frappe.DoesNotExistError)
    except Exception as ex:
        frappe.throw(_("An error has occurred"))
