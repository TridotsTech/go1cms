import frappe
from frappe import _, local
from premailer import transform
from datetime import datetime
from go1_cms.api.website.log_page import (
    log_page_view
)


@frappe.whitelist()
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
    data_insert = {}
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
    doc.send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # insert contact
    doc.insert()

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
            doc_lead.insert()

    # send email
    if cms_settings.allow_send_email_contact and cms_settings.list_email_receipt:
        list_email = cms_settings.list_email_receipt
        recipients = [e.strip()
                      for e in str(cms_settings.list_email_receipt).split(';')]
        subject = f"Nhận được một liên hệ mới {doc.email or ''} - {doc.phone_number or ''}"

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            template="email_send_contact",
            args=doc.as_dict(),
            # now=True,
        )

    frappe.enqueue(log_page_view, queue='default', ip=local.request.remote_addr,
                   form_type="Form liên hệ")
    return {"name": doc.name}


@frappe.whitelist()
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
def delete_contact(name):
    if not frappe.db.exists("MBW Contact", name):
        frappe.throw(_("Contact not found"), frappe.DoesNotExistError)

    frappe.delete_doc('MBW Contact', name)

    result = {'name': name}
    return result
