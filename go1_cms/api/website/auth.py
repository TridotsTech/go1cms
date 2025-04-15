import frappe
from frappe import _, local
from frappe.utils import now, add_to_date
from datetime import datetime
from frappe.utils import (
    validate_email_address,
)
from go1_cms.api.common import (
    validate_password,
    send_email_manage,
    send_email_customer,
    get_domain
)
from webshop.webshop.doctype.webshop_settings.webshop_settings import (
    get_shopping_cart_settings,
)
from frappe.utils.nestedset import get_root_of

from frappe.auth import LoginManager
from frappe.contacts.doctype.contact.contact import get_contact_name
from frappe.contacts.doctype.address.address import get_address_display


@frappe.whitelist(methods=['POST'], allow_guest=True)
def login(usr, pwd):
    login_manager = LoginManager()
    login_manager.authenticate(usr, pwd)
    login_manager.post_login()

    return {"user": usr}


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
            frappe.throw('Họ và tên không được để trống')

        if not phone_number:
            frappe.throw('Số điện thoại không được để trống')

        if frappe.db.exists("User", email):
            return frappe.throw('Email đã được đăng ký', frappe.DuplicateEntryError)
        if frappe.db.exists("User", {"mobile_no": phone_number}):
            return frappe.throw('Số điện thoại đã được đăng ký', frappe.DuplicateEntryError)

        # create user
        new_doc = frappe.new_doc('User')
        new_doc.email = email
        new_doc.first_name = full_name
        new_doc.mobile_no = phone_number
        new_doc.send_welcome_email = 0
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

        ### send email ###
        domain = get_domain()
        args = {
            'time': new_doc.creation.strftime("%d/%m/%Y %H:%M:%S"),
            'full_name': full_name,
            'phone_number': phone_number,
            'email': email
        }
        # manage
        args['redirect_to'] = f'{domain}/app/user/{new_doc.name}'
        send_email_manage(None, 'email_register_manage', args)
        # customer
        args['redirect_to'] = f'{domain}/dang-nhap'
        send_email_customer(None, 'email_register_customer', [email], args)

        frappe.enqueue(
            "go1_cms.api.website.auth.create_info_after_create_user",
            info_user={"email": email, "full_name": full_name,
                       "phone_number": phone_number},
            now=True,
            enqueue_after_commit=True,
        )

        # delete captcha
        frappe.db.delete("CMS Captcha", {'name': captcha.name})

        return {'status': '200', 'name': new_doc.name}
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) in [frappe.ValidationError, frappe.DuplicateEntryError]:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw(_('An error has occurred'))


def create_info_after_create_user(info_user={}):
    full_name = info_user.get('full_name')
    email = info_user.get('email')
    phone_number = info_user.get('phone_number')

    # create customer
    customer = create_customer(full_name)

    # create contact
    contact = create_contact(full_name, email, customer.name)

    # create address
    address = create_address(full_name, email, phone_number, customer.name)

    # update customer
    address_display = get_address_display(address.as_dict())

    customer.reload()
    customer.customer_primary_contact = contact.name
    customer.customer_primary_address = address.name
    customer.primary_address = address_display
    customer.save(ignore_permissions=True)


def create_customer(full_name):
    customer = frappe.new_doc("Customer")
    customer.update(
        {
            "customer_name": full_name,
            "customer_type": "Individual",
            "customer_group": get_shopping_cart_settings().default_customer_group,
            "territory": get_root_of("Territory"),
        }
    )
    customer.append("portal_users", {"user": frappe.session.user})
    customer.insert(ignore_permissions=True, ignore_mandatory=True)

    return customer


def create_contact(full_name, email, customer_name):
    contact_name = get_contact_name(email)
    if not contact_name:
        contact = frappe.new_doc("Contact")
        contact.update(
            {
                "first_name": full_name,
                "email_ids": [{"email_id": email, "is_primary": 1}]
            }
        )
        contact.append("links", dict(
            link_doctype="Customer", link_name=customer_name))
        contact.insert(ignore_permissions=True, ignore_mandatory=True)
    else:
        contact = frappe.get_doc("Contact", contact_name)
        if not frappe.db.exists("Dynamic Link", {"parent": contact_name, "link_doctype": "Customer", "link_name": customer_name, "parenttype": "Contact"}):
            contact.append("links", dict(
                link_doctype="Customer", link_name=customer_name))
            contact.save(ignore_permissions=True)
    return contact


def create_address(full_name, email, phone_number, customer_name):
    address_name = frappe.db.get_value('Dynamic Link', {
        'link_doctype': 'Customer', 'link_name': customer_name, 'parenttype': 'Address'}, ['parent'])
    if not address_name:
        address = frappe.new_doc("Address")
        address.address_title = full_name
        address.email_id = email
        address.phone = phone_number
        address.append("links", dict(
            link_doctype="Customer", link_name=customer_name))
        address.insert(ignore_permissions=True, ignore_mandatory=True)
        return address
    else:
        doc = frappe.get_doc("Address", address_name)
        if not doc.address_title:
            doc.address_title = full_name
        if not doc.email_id:
            doc.email_id = email
        if not doc.phone:
            doc.phone = phone_number
        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True
        doc.save()
        return doc
