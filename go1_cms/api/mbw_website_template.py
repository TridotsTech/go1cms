import frappe
from frappe import _
from pypika import Criterion


@frappe.whitelist()
def get_web_templates(repo):
    WebTemplate = frappe.qb.DocType("MBW Website Template")
    query = (
        frappe.qb.from_(WebTemplate)
        .select("*")
    )
    if repo != 'Tất cả':
        query = query.where(WebTemplate.type_template == repo)

    templates = query.run(as_dict=True)
    return templates


@frappe.whitelist()
def get_web_template(name):
    WebTemplate = frappe.qb.DocType("MBW Website Template")
    query = (
        frappe.qb.from_(WebTemplate)
        .select("*")
        .where(WebTemplate.name == name)
    ).limit(1)

    template = query.run(as_dict=True)
    if not len(template):
        frappe.throw(_("Template not found"), frappe.DoesNotExistError)
    template = template.pop()
    return template


@frappe.whitelist()
def add_web_template(name):
    template = frappe.get_doc("MBW Website Template", name)
    if not template:
        frappe.throw(_("Template not found"), frappe.DoesNotExistError)

    MBWClientWebsite = frappe.qb.DocType("MBW Client Website")
    website = frappe.new_doc("MBW Client Website")
    website.name_web = template.name
    website.save(ignore_permissions=True)

    return website.name
