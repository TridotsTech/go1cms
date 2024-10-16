import frappe
from frappe import _
from webshop.webshop.shopping_cart.cart import (
    decorate_quotation_doc
)
from frappe.contacts.doctype.contact.contact import get_contact_name
from frappe.utils import cint, cstr, flt, get_fullname
from webshop.webshop.doctype.webshop_settings.webshop_settings import (
    get_shopping_cart_settings,
)
from frappe.utils.nestedset import get_root_of
from go1_cms.api.website.auth import (
    create_customer,
    create_contact,
    create_address
)
from frappe.contacts.doctype.address.address import get_address_display
from webshop.webshop.shopping_cart.cart import (
    get_party,
    _get_cart_quotation,
    update_cart as update_cart_default,
    request_for_quotation
)
from go1_cms.api.common import (
    send_email_manage,
    send_email_customer,
    get_domain
)
import json
from erpnext.selling.doctype.quotation.quotation import _make_sales_order


@frappe.whitelist(methods=['POST'])
def get_cart():
    customer = get_customer()
    quotation = _get_cart_quotation()

    return decorate_quotation_doc(quotation)


@frappe.whitelist(methods=['POST'])
def create_order(**kwargs):
    full_name = kwargs.get('full_name')
    email = kwargs.get('email')
    phone_number = kwargs.get('phone_number')
    address = kwargs.get('address')

    quotation = _get_cart_quotation()
    if quotation.name and not quotation.get('__islocal'):
        if not full_name:
            frappe.throw('Họ tên không được để trống')
        if not email:
            frappe.throw('Email không được để trống')
        if not phone_number:
            frappe.throw('Số điện thoại không được để trống')
        if not address:
            frappe.throw('Địa chỉ không được để trống')

        # create new contact
        contact = create_new_address_order({
            "address_title": full_name,
            "email_id": email,
            "phone": phone_number,
            "address_line1": address
        })
        update_address_quotation(quotation, contact.name)

        quotation_name = request_for_quotation()

        sale_order = _make_sales_order(
            source_name=quotation_name, ignore_permissions=True)
        sale_order.payment_schedule = []
        sale_order.save(ignore_permissions=True)
        
        ### send email ###
        # manage
        sale_order.reload()
        domain = get_domain()
        d_t = sale_order.creation.strftime("%d-%m-%Y %H:%M:%S")
        subject = f"Một đơn hàng mới tạo lúc {d_t}"
        redirect_to = f'{domain}/app/sales-order/{sale_order.name}'

        args = {
            'order_code': sale_order.name,
            'redirect_to': redirect_to,
        }
        send_email_manage(subject, 'email_order_manage', args)
        # customer
        subject = f'Đơn hàng của bạn đã được tạo thành công vào lúc {d_t}'
        redirect_to = f'{domain}/tai-khoan?tag=my-orders'
        items = []
        for item in sale_order.items:
            items.append({
                'item_name': item.item_name,
                'qty': item.qty,
                'uom': item.uom,
                'rate': item.rate,
                'amount': item.amount,
            })
        args = {
            'order_code': sale_order.name,
            'redirect_to': redirect_to,
            'items': items,
            'grand_total': sale_order.grand_total
        }
        send_email_customer(subject, 'email_order_customer', [email], args)
        
        if hasattr(frappe.local, "cookie_manager"):
            frappe.local.cookie_manager.delete_cookie("cart_count")
            frappe.local.cookie_manager.delete_cookie("cart")
    else:
        frappe.throw("Không thể tạo đơn hàng")

    return quotation_name


@frappe.whitelist()
def update_cart(item_code, qty, additional_notes=None, add_item=False):
    customer = get_customer()
    qty = flt(qty)
    
    if add_item:
        quotation = _get_cart_quotation()
        quotation_items = quotation.get("items", {"item_code": item_code})
        if quotation_items:
            qty = quotation_items[0].qty + qty

    if qty > 999:
        qty = 999
    rs = update_cart_default(item_code, qty, additional_notes=additional_notes,
                             with_items=1)
    quotation = _get_cart_quotation()
    quotation = update_address_quotation(
        quotation, customer.customer_primary_address)

    cart_cookie = {
        "items": [{"item_code": item.item_code, "item_name": item.item_name, "qty": item.qty, "amount": item.amount, "rate": item.rate, "uom": item.uom, "image": item.image} for item in quotation.items],
        "grand_total": quotation.grand_total
    }
    cart_cookie = json.dumps(cart_cookie, ensure_ascii=False)
    if hasattr(frappe.local, "cookie_manager"):
        frappe.local.cookie_manager.set_cookie("cart", cart_cookie)

    return quotation.name


def create_new_address_order(info={}):
    customer = get_customer()
    address = frappe.new_doc("Address")
    address.update(
        info
    )
    address.append("links", dict(
        link_doctype="Customer", link_name=customer.name))
    address.insert(ignore_permissions=True, ignore_mandatory=True)
    # update primary address customer
    customer.customer_primary_address = address.name
    customer.flags.ignore_permissions = True
    customer.flags.ignore_mandatory = True
    customer.save()
    return address


def update_address_quotation(quot, address_name):
    address_doc = frappe.get_doc("Address", address_name).as_dict()

    if quot.customer_address != address_name:
        quot.customer_address = address_name
        quot.address_display = get_address_display(address_doc)
    if quot.shipping_address_name != address_name:
        quot.shipping_address_name = address_name
        quot.shipping_address = get_address_display(address_doc)

    if not quot.get('__islocal'):
        quot.save(ignore_permissions=True)
    return quot


def get_customer():
    user = frappe.session.user
    if user == 'Guest':
        return None

    user_email, phone_number = frappe.db.get_value(
        'User', user, ['email', 'mobile_no'])
    contact_name = get_contact_name(user_email)
    party = None

    if contact_name:
        contact = frappe.get_doc("Contact", contact_name)
        if contact.links:
            party_doctype = contact.links[0].link_doctype
            party = contact.links[0].link_name

    if party:
        doc = frappe.get_doc(party_doctype, party)
        if doc.doctype in ["Customer", "Supplier"]:
            check_update = False
            if not frappe.db.exists("Portal User", {"parent": doc.name, "user": user}):
                doc.append("portal_users", {"user": user})
                check_update = True

            if not doc.customer_primary_contact:
                check_update = True
                contact = create_contact(fullname, user_email, doc.name)
                doc.customer_primary_contact = contact.name
            if not doc.customer_primary_address:
                check_update = True
                address = create_address(fullname, user_email,
                                         phone_number, doc.name)
                customer.customer_primary_address = address.name

            if check_update:
                doc.flags.ignore_permissions = True
                doc.flags.ignore_mandatory = True
                doc.save()

        return doc

    else:
        fullname = get_fullname(user)
        customer = create_customer(fullname)
        contact = create_contact(fullname, user_email, customer.name)
        address = create_address(fullname, user_email,
                                 phone_number, customer.name)

        # update customer
        address_display = get_address_display(address.as_dict())
        customer.customer_primary_contact = contact.name
        customer.customer_primary_address = address.name
        customer.primary_address = address_display
        customer.save(ignore_permissions=True)

        return customer
