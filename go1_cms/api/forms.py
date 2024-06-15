import frappe
from frappe import _


@frappe.whitelist()
def get_form(name):
    MBWForm = frappe.qb.DocType("MBW Form")
    query = (
        frappe.qb.from_(MBWForm)
        .select("*")
        .where(MBWForm.name == name)
    ).limit(1)

    mbw_form = query.run(as_dict=True)
    if not len(mbw_form):
        frappe.throw(_("Không tìm thấy biểu mẫu"), frappe.DoesNotExistError)
    mbw_form = mbw_form.pop()

    form_fields = frappe.db.get_all("MBW Form Item", filters={"parent": name, "parentfield": "form_fields"}, fields=[
        'name', 'field_label', 'field_name', 'field_placeholder', 'field_type', 'field_mandatory', 'field_hidden', 'field_options', 'max_file_size', 'idx'
    ], order_by="idx")
    mbw_form['form_fields'] = form_fields
    return mbw_form


@frappe.whitelist()
def update_form(data):
    doc_name = data.get('name')
    form_name = data.get('form_name')
    if not frappe.db.exists("MBW Form", doc_name):
        frappe.throw(_("Không tìm thấy biểu mẫu"), frappe.DoesNotExistError)

    if not form_name:
        frappe.throw(_("Tên biểu mẫu không được để trống"))

    doc = frappe.get_doc('MBW Form', doc_name)

    for field in data.get('form_fields'):
        f_doc_name = field.get('name')
        data_update = {
            'idx': field.get('idx'),
            'field_label': field.get('field_label'),
            'field_mandatory': field.get('field_mandatory'),
            'field_hidden': field.get('field_hidden'),
            'field_options': field.get('field_options'),
            'field_placeholder': field.get('field_placeholder'),
            'max_file_size': field.get('max_file_size'),
        }
        # update form item
        frappe.db.set_value('MBW Form Item', f_doc_name, data_update)

    doc.reload()
    doc.form_name = form_name
    doc.btn_text = data.get('btn_text')
    doc.save()

    result = {'name': doc.name}
    return result
