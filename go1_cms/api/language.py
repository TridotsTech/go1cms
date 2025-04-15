import frappe


@frappe.whitelist()
def get_language():
    return frappe.db.get_value('User', frappe.session.user, 'language') or 'en'


@frappe.whitelist()
def change_language(lang):
    language = frappe.db.get_value('Language', lang, 'name')
    if language:
        frappe.db.set_value('User', frappe.session.user, {
            'language': lang
        })
        return lang
    else:
        frappe.throw('Language not found')
