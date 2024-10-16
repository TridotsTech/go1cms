import frappe
from frappe import _, local
from webshop.webshop.shopping_cart.cart import (
    get_party
)
from go1_cms.api.website.cart import (
    get_customer
)
from frappe.core.doctype.user.user import User
from go1_cms.api.common import (
    validate_password
)
from passlib.context import CryptContext
from frappe.query_builder import Table

Auth = Table("__Auth")
passlibctx = CryptContext(
    schemes=[
        "pbkdf2_sha256",
        "argon2",
    ],
)


@frappe.whitelist(methods=['POST'])
def get_accout_info():
    if frappe.session.user == "Guest":
        return {}

    customer = get_customer()
    info_account = {}

    users = frappe.get_all("User",
                           fields=["first_name as full_name",
                                   "email", "mobile_no", "location"],
                           filters={'name': frappe.session.user}, limit=1)
    if users:
        info_account['account_info'] = users[0]

    if customer.customer_primary_address:
        address_info = frappe.db.get_value(
            'Address', customer.customer_primary_address, ['address_title as full_name', 'email_id as email', 'address_line1', 'phone'], as_dict=1)
        info_account['address_info'] = address_info
    return info_account


@frappe.whitelist(methods=['POST'])
def update_accout_info(**kwargs):
    account_info = kwargs.get('account_info')
    address_info = kwargs.get('address_info')

    if type(account_info) == dict:
        check_update = False
        user = frappe.get_doc('User', frappe.session.user)
        full_name = account_info.get("full_name")
        location = account_info.get("location")
        mobile_no = account_info.get("mobile_no")
        if full_name and full_name != user.first_name:
            user.first_name = full_name
            check_update = True
        if location and location != user.location:
            user.location = location
            check_update = True
        if mobile_no and user.mobile_no != mobile_no:
            if frappe.db.exists("User", {"mobile_no": mobile_no}):
                return frappe.throw('Số điện thoại đã được đăng ký', frappe.DuplicateEntryError)
            user.mobile_no = mobile_no
            check_update = True
            
        if check_update:
            user.save(ignore_permissions=True)

    if address_info:
        customer = get_customer()
        if customer.customer_primary_address:
            address = frappe.get_doc(
                "Address", customer.customer_primary_address)
            address.address_title = address_info.get('full_name')
            address.email_id = address_info.get('email')
            address.address_line1 = address_info.get('address_line1')
            address.phone = address_info.get('phone')
            address.flags.ignore_permissions = True
            address.flags.ignore_mandatory = True
            address.save()

    return {'user': frappe.session.user}


@frappe.whitelist(methods=['POST'])
def reset_password(old_pwd, new_pwd):

    if not new_pwd:
        frappe.throw('Mật khẩu không được để trống')

    if validate_password(new_pwd):
        frappe.throw(validate_password(new_pwd))

    if not check_password(frappe.session.user, old_pwd):
        frappe.throw('Mật khẩu không chính xác')

    user = frappe.get_doc('User', frappe.session.user)
    user.flags.ignore_password_policy = True
    user.new_password = new_pwd
    user.save(ignore_permissions=True)

    return {'user': frappe.session.user}


def check_password(user, pwd, doctype="User", fieldname="password"):
    result = (
        frappe.qb.from_(Auth)
        .select(Auth.name, Auth.password)
        .where(
            (Auth.doctype == doctype)
            & (Auth.name == user)
            & (Auth.fieldname == fieldname)
            & (Auth.encrypted == 0)
        )
        .limit(1)
        .run(as_dict=True)
    )
    if not result or not passlibctx.verify(pwd, result[0].password):
        return False

    return True
