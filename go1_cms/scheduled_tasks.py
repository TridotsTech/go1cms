import frappe
from frappe.utils import now, add_to_date


def delete_old_captcha():
    old_datetime = add_to_date(now(), minutes=-10)
    old_tasks = frappe.get_all(
        'CMS Captcha', filters={'modified': ['<', old_datetime]}, fields=['name'])

    current_user = frappe.session.user
    try:
        frappe.set_user('Administrator')
        for task in old_tasks:
            frappe.delete_doc('CMS Captcha', task.name)
        frappe.db.commit()
    finally:
        frappe.set_user(current_user)

    return len(old_tasks)
