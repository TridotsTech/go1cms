from mimetypes import guess_type

import frappe
from frappe import _
from frappe.utils import cint
from frappe.handler import is_whitelisted
from frappe.utils.image import optimize_image


@frappe.whitelist(allow_guest=True)
def upload_file():
    if frappe.session.user == "Guest":
        return
    files = frappe.request.files
    is_private = frappe.form_dict.is_private
    doctype = frappe.form_dict.doctype
    docname = frappe.form_dict.docname
    fieldname = frappe.form_dict.fieldname
    file_url_old = frappe.form_dict.file_url_old
    file_url = frappe.form_dict.file_url
    folder = frappe.form_dict.folder or "Home"
    method = frappe.form_dict.method
    filename = frappe.form_dict.file_name
    optimize = frappe.form_dict.optimize
    content = None

    if "file" in files:
        file = files["file"]
        content = file.stream.read()
        filename = file.filename

        content_type = guess_type(filename)[0]
        if optimize and content_type and content_type.startswith("image/"):
            args = {"content": content, "content_type": content_type}
            if frappe.form_dict.max_width:
                args["max_width"] = int(frappe.form_dict.max_width)
            if frappe.form_dict.max_height:
                args["max_height"] = int(frappe.form_dict.max_height)
            content = optimize_image(**args)

    frappe.local.uploaded_file = content
    frappe.local.uploaded_filename = filename

    if method:
        method = frappe.get_attr(method)
        is_whitelisted(method)
        return method()
    else:
        ret = frappe.get_doc(
            {
                "doctype": "File",
                "attached_to_doctype": doctype,
                "attached_to_name": docname,
                "attached_to_field": fieldname,
                "folder": folder,
                "file_name": filename,
                "file_url": file_url,
                "is_private": cint(is_private),
                "content": content,
            }
        )
        ret.save()

        if file_url_old and file_url_old not in ['undefined', 'null']:
            if frappe.db.exists("File", {"file_url": file_url_old, "attached_to_doctype": doctype, "attached_to_name": docname, "attached_to_field": fieldname}):
                doc_file_old = frappe.get_last_doc(
                    'File', filters={"file_url": file_url_old, "attached_to_doctype": doctype, "attached_to_name": docname, "attached_to_field": fieldname})
                frappe.delete_doc('File', doc_file_old.name)
        return ret
