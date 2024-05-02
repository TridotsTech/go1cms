import frappe
from frappe import _


@frappe.whitelist()
def get_footer_component_info(footer_component_name):
    footer_component = frappe.get_doc("Footer Component", footer_component_name)

    cp_fc_content = footer_component.get("cp_fc_content")
    cp_sc_content = footer_component.get("cp_sc_content")
    web_section = footer_component.get("web_section")
    section_name = []
    for i in range(len(web_section)):
        section_name.append(web_section[i].get("section"))

    return {
        "First column content": cp_fc_content,
        "Second column content": cp_sc_content,
        "Web section": web_section
    }


@frappe.whitelist()
def update_footer_component_info(footer_component_name, **kwargs):
    footer_component = frappe.get_doc("Footer Component", footer_component_name)

    for key, value in kwargs.items():
        if hasattr(footer_component, key):
            setattr(footer_component, key, value)

    footer_component.save()
    frappe.db.commit()

    return "Cập nhật Footer thành công!"

