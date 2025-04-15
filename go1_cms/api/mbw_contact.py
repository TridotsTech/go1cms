import frappe
from frappe import _, local
from premailer import transform
from datetime import datetime
from go1_cms.api.website.log_page import (
    log_page_view
)
from go1_cms.api.wrapper_api import (
    check_user_admin
)
from go1_cms.api.common import (
    send_email_manage,
    get_domain
)


@frappe.whitelist()
@check_user_admin
def get_contact(name):
    MbwContact = frappe.qb.DocType("MBW Contact")
    query = (
        frappe.qb.from_(MbwContact)
        .select("*")
        .where(MbwContact.name == name)
    ).limit(1)

    contact = query.run(as_dict=True)
    if not len(contact):
        frappe.throw(_("Contact not found"), frappe.DoesNotExistError)
    contact = contact.pop()
    return contact


@frappe.whitelist(allow_guest=True)
def create_contact(**kwargs):
    # if not frappe.db.exists('Page Section', kwargs.get('name_section')):
    #     frappe.throw(_("Không thể gửi liên hệ"), frappe.DoesNotExistError)

    # page_st = frappe.get_value(
    #     "Page Section", kwargs.get('name_section'), ['form'], as_dict=1)
    # form_fields = frappe.db.get_all("MBW Form Item", filters={'parent': page_st.form}, fields=[
    #     'field_label', 'field_name', 'field_hidden', 'field_mandatory'
    # ])
    # for f in form_fields:
    #     if f.field_hidden == 0 and f.field_mandatory == 1 and not kwargs.get(f.field_name):
    #         frappe.throw(f"{f.field_label} không được để trống")

    doc = frappe.new_doc("MBW Contact")
    doc.last_name = kwargs.get("last_name") or ''
    doc.first_name = kwargs.get("first_name") or ''
    if kwargs.get("full_name"):
        doc.full_name = kwargs.get("full_name")
    else:
        doc.full_name = " ".join(
            [n for n in [doc.last_name, doc.first_name] if n])
    doc.email = kwargs.get("email") or ''
    doc.phone_number = kwargs.get("phone_number") or ''
    doc.address = kwargs.get("address") or ''
    doc.message = kwargs.get("message") or ''
    doc.source = kwargs.get("source") or ''
    doc.utm_source = kwargs.get("utm_source") or ''
    doc.utm_campaign = kwargs.get("utm_campaign") or ''
    doc.sent_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # insert contact
    doc.insert(ignore_permissions=True)

    cms_settings = frappe.get_single('CMS Settings')
    # sync data leads
    if cms_settings.sync_lead_data and 'crm' in frappe.get_installed_apps() and frappe.db.exists({"doctype": "DocType", "name": "CRM Lead"}):
        lead_status = frappe.get_all('CRM Lead Status', filters={
                                     'name': ('IN', ['Mới', 'New'])}, pluck='name')
        if lead_status:
            doc_lead = frappe.new_doc("CRM Lead")
            doc_lead.first_name = doc.full_name.strip() or 'Mới'
            doc_lead.lead_name = doc.full_name.strip() or 'Mới'
            doc_lead.email = doc.email or ''
            doc_lead.mobile_no = doc.phone_number or ''
            if doc.utm_source and frappe.db.exists({"doctype": "CRM Lead Source", "name": doc.utm_source}):
                doc_lead.source = doc.utm_source
            if 'Mới' in lead_status:
                doc_lead.status = 'Mới'
            elif 'New' in lead_status:
                doc_lead.status = 'New'
            # insert lead
            doc_lead.insert(ignore_permissions=True)

    # send email
    domain = get_domain()
    doc.reload()
    args = {
        'time': doc.creation.strftime("%d/%m/%Y %H:%M:%S"),
        'full_name': doc.full_name,
        'phone_number': doc.phone_number,
        'email': doc.email,
        'address': doc.address,
        'content': doc.message,
        'source': doc.source,
        'utm_source': doc.utm_source,
        'utm_campaign': doc.utm_campaign,
        'sent_time': doc.sent_time.strftime("%d/%m/%Y %H:%M:%S"),
        'redirect_to': f'{domain}/cms/contacts/{doc.name}'
    }
    send_email_manage(None, "email_send_contact", args)

    frappe.enqueue(log_page_view, queue='default', ip=local.request.remote_addr,
                   form_type="Form liên hệ")
    return {"name": doc.name}


@frappe.whitelist()
@check_user_admin
def update_contact(data):
    doc_name = data.get('name')
    if not frappe.db.exists("MBW Contact", doc_name):
        frappe.throw(_("Contact not found"), frappe.DoesNotExistError)

    doc = frappe.get_doc('MBW Contact', doc_name)
    doc.full_name = data.get('full_name')
    doc.last_name = data.get('last_name')
    doc.first_name = data.get('first_name')
    doc.email = data.get('email')
    doc.phone_number = data.get('phone_number')
    doc.message = data.get('message')
    doc.save()

    result = {'name': doc.name}
    return result


@frappe.whitelist()
@check_user_admin
def delete_contact(name):
    if not frappe.db.exists("MBW Contact", name):
        frappe.throw(_("Contact not found"), frappe.DoesNotExistError)

    frappe.delete_doc('MBW Contact', name)

    result = {'name': name}
    return result
