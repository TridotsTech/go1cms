import frappe
from frappe import _
from premailer import transform


@frappe.whitelist(allow_guest=True)
def create_contact(**kwargs):
    data_insert = {}
    doc = frappe.new_doc("MBW Contact")

    if kwargs.get("full_name"):
        doc.full_name = kwargs.get("full_name")
    if kwargs.get("last_name"):
        doc.last_name = kwargs.get("last_name")
    if kwargs.get("first_name"):
        doc.first_name = kwargs.get("first_name")
    if kwargs.get("email"):
        doc.email = kwargs.get("email")
    if kwargs.get("phone_number"):
        doc.phone_number = kwargs.get("phone_number")
    if kwargs.get("address"):
        doc.address = kwargs.get("address")
    if kwargs.get("message"):
        doc.message = kwargs.get("message")
    # insert contact
    doc.insert()

    kwargs["full_name"] = kwargs.get(
        "full_name") or kwargs.get("first_name", '')

    cms_settings = frappe.get_single('CMS Settings')
    # sync data leads
    if cms_settings.sync_lead_data and frappe.db.exists({"doctype": "DocType", "name": "CRM Lead"}):
        lead_status = frappe.get_all('CRM Lead Status', filters={
                                     'name': ('IN', ['Mới', 'New'])}, pluck='name')
        if lead_status:
            doc_lead = frappe.new_doc("CRM Lead")
            full_name = ''
            if kwargs.get("full_name"):
                full_name = kwargs.get("full_name")
            else:
                full_name = [n for n in [kwargs.get(
                    "last_name"), kwargs.get("first_name")] if n]
                full_name = " ".join(full_name)
            doc_lead.first_name = full_name.strip() or 'Mới'
            doc_lead.lead_name = full_name.strip()
            doc_lead.email = kwargs.get("email", '')
            doc_lead.mobile_no = kwargs.get("phone_number", '')
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
        subject = f"[MBW CMS] - Đã nhận được một liên hệ mới từ {kwargs.get('email') or ''}"

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            template="email_send_contact",
            args=kwargs,
            # now=True,
        )

    return {"name": doc.name}
