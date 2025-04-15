import frappe
from frappe.translate import get_all_translations


@frappe.whitelist(allow_guest=True)
def get_translations(lang=None):
    if lang:
        language = lang
    else:
        if frappe.session.user != "Guest":
            language = frappe.db.get_value(
                "User", frappe.session.user, "language")
        else:
            language = frappe.db.get_single_value(
                "System Settings", "language")
    return get_all_translations(language)


def check_app_permission():
    if frappe.session.user == "Administrator":
        return True

    return False
