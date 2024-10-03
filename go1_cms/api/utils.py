import frappe

def clear_cookie_cart():
    if hasattr(frappe.local, "cookie_manager"):
        frappe.local.cookie_manager.delete_cookie("cart")
        frappe.local.cookie_manager.delete_cookie("cart_count")