import frappe
from frappe import _
from frappe.auth import LoginManager


@frappe.whitelist(methods=['POST'], allow_guest=True)
def login(usr, pwd):
    login_manager = LoginManager()
    login_manager.authenticate(usr, pwd)
    login_manager.get_user_info()
    if login_manager.user_type != "System User":
        frappe.throw(_('Email hoặc mật khẩu không chính xác.'),
                     frappe.AuthenticationError)
    login_manager.post_login()

    return {"user": usr}


@frappe.whitelist(allow_guest=True)
def oauth_providers():
    from frappe.utils.html_utils import get_icon_html
    from frappe.utils.password import get_decrypted_password
    from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys

    out = []
    providers = frappe.get_all(
        "Social Login Key",
        filters={"enable_social_login": 1},
        fields=["name", "client_id", "base_url", "provider_name", "icon"],
        order_by="name",
    )

    for provider in providers:
        client_secret = get_decrypted_password(
            "Social Login Key", provider.name, "client_secret")
        if not client_secret:
            continue

        icon = None
        if provider.icon:
            if provider.provider_name == "Custom":
                icon = get_icon_html(provider.icon, small=True)
            else:
                icon = f"<img src='{provider.icon}' alt={provider.provider_name}>"

        if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
            out.append(
                {
                    "name": provider.name,
                    "provider_name": provider.provider_name,
                    "auth_url": get_oauth2_authorize_url(provider.name, "/cms"),
                    "icon": icon,
                }
            )
    return out
