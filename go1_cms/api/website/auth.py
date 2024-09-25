import frappe
from frappe import _, local
from frappe.utils import now, add_to_date
from datetime import datetime
from frappe.utils import (
    validate_email_address,
)
from go1_cms.api.common import (
    validate_password
)
from webshop.webshop.doctype.webshop_settings.webshop_settings import (
    get_shopping_cart_settings,
)
from frappe.utils.nestedset import get_root_of


@frappe.whitelist(methods=['POST'], allow_guest=True)
def sign_up(**kwargs):
    try:
        captcha_text = kwargs.get('captcha_text', None)
        ip = local.request.remote_addr

        # verify captcha
        captcha = frappe.db.get_value('CMS Captcha', {
            "ip": ip, 'captcha_text': captcha_text}, ['name', 'creation'], as_dict=1)
        if not captcha_text or not captcha:
            return {
                'status': '0',
                'msg': 'Mã captcha không đúng'
            }

        old_datetime = datetime.strptime(
            add_to_date(now(), minutes=-10), "%Y-%m-%d %H:%M:%S.%f")
        if old_datetime >= captcha.creation:
            return {
                'status': '1',
                'msg': 'Mã captcha đã hết hạn'
            }

        # sign up
        email = kwargs.get('email', '').strip()
        password = kwargs.get('password', '').strip()
        full_name = kwargs.get('full_name', '').strip()
        phone_number = kwargs.get('phone_number', '').strip()
        # check email
        if not email:
            frappe.throw('Email không được để trống')
        if not validate_email_address(email):
            frappe.throw('Email không đúng định dạng')
        # check password
        if not password:
            frappe.throw('Mật khẩu không được để trống')
        if validate_password(password):
            frappe.throw(validate_password(password))

        if not full_name:
            frappe.throw('Họ tên không được để trống')

        if frappe.db.exists("User", email):
            return frappe.throw('Email đã tồn tại', frappe.DuplicateEntryError)

        # create user
        new_doc = frappe.new_doc('User')
        new_doc.email = email
        new_doc.first_name = full_name
        new_doc.save(ignore_permissions=True)
        new_doc.reload()
        if frappe.db.exists("Role", 'Customer'):
            new_doc.update(
                {
                    "roles": [{"role": 'Customer'}]
                }
            )
        new_doc.flags.ignore_password_policy = True
        new_doc.new_password = password
        new_doc.save(ignore_permissions=True)

        # create customer
        customer = frappe.new_doc("Customer")
        customer.update(
            {
                "customer_name": full_name,
                "customer_type": "Individual",
                "customer_group": get_shopping_cart_settings().default_customer_group,
                "territory": get_root_of("Territory"),
            }
        )
        customer.append("portal_users", {"user": new_doc.name})
        customer.flags.ignore_mandatory = True
        customer.insert(ignore_permissions=True)

        # create contact
        contact = frappe.new_doc("Contact")
        contact.update(
            {"first_name": full_name, "email_ids": [
                {"email_id": new_doc.name, "is_primary": 1}]}
        )
        contact.append("links", dict(
            link_doctype="Customer", link_name=customer.name))
        contact.flags.ignore_mandatory = True
        contact.insert(ignore_permissions=True)

        # delete captcha
        frappe.db.delete("CMS Captcha", {'name': captcha.name})

        return {'status': '200', 'name': new_doc.name}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) in [frappe.ValidationError, frappe.DuplicateEntryError]:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Có lỗi xảy ra')
