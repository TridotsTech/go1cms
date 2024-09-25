import frappe
from frappe import _, local
from datetime import datetime
from io import BytesIO
from captcha.image import ImageCaptcha
import string
import random
import base64
from frappe.utils import now, add_to_date


@frappe.whitelist(methods=['GET'], allow_guest=True)
def get_captcha():
    captcha = ImageCaptcha()
    captcha_text = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6))
    data = BytesIO()
    captcha.write(captcha_text, data)
    data.seek(0)

    # Chuyển đổi dữ liệu hình ảnh sang Base64
    image_base64 = base64.b64encode(data.getvalue()).decode('utf-8')
    ip = local.request.remote_addr

    # delete captcha old
    old_datetime = add_to_date(now(), minutes=-10)
    frappe.db.delete("CMS Captcha", {
        "creation": ("<", old_datetime),
        "ip": ip
    })

    # create new captcha
    new_doc = frappe.new_doc('CMS Captcha')
    new_doc.ip = ip
    new_doc.captcha_text = captcha_text
    new_doc.captcha_image = image_base64
    new_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        'captcha_image': "data:image/png;base64," + image_base64,
    }
