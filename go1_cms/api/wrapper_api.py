import frappe
import functools


def check_user_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if frappe.session.user != "Guest":
            users = frappe.get_all("User", fields=["name", "user_type"], filters={
                'name': frappe.session.user}, limit=1)
            if users and users[0].user_type == "System User":
                return func(*args, **kwargs)
        frappe.throw('Không được phép truy cập', frappe.PermissionError)
        return None

    return wrapper
