import frappe
from frappe import _


@frappe.whitelist()
def get_header_component_info(header_component_name):
    header_component = frappe.get_doc("Header Component", header_component_name)

    button_text = header_component.get("button_text")
    button_link = header_component.get("button_link")
    web_section = header_component.get("web_section")
    return {
        "Button text": button_text,
        "Button link": button_link,
        "Web section": web_section
    }


@frappe.whitelist()
def update_header_component_info(header_component_name, **kwargs):
    header_component = frappe.get_doc("Header Component", header_component_name)

    for key, value in kwargs.items():
        if hasattr(header_component, key):
            setattr(header_component, key, value)

    header_component.save()
    frappe.db.commit()

    return "Cập nhật Header thành công!"
