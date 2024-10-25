import frappe

from go1_cms.api.common import (
    send_email_customer,
    get_domain,
    ORDER_STATUS
)


def send_mail_sale_order(doc, method):
    try:
        if doc.status in ['To Deliver and Bill', 'To Bill', 'To Deliver'] and doc.cms_send_mail_delivery:
            doc.db_set('cms_send_mail_delivery', 0)
            # send mail customer
            args = get_args_order(doc)
            send_email_customer(
                None, 'email_delivery_order_customer', [args.get('email')], args)
        elif doc.status in ['Completed', 'Closed'] and doc.cms_send_mail_completed:
            doc.db_set('cms_send_mail_completed', 0)
            # send mail customer
            args = get_args_order(doc)
            send_email_customer(
                None, 'email_order_success_customer', [args.get('email')], args)
        elif doc.status == "Cancelled" and doc.cms_send_mail_cancelled:
            doc.db_set('cms_send_mail_cancelled', 0)
            # send mail customer
            args = get_args_order(doc)
            send_email_customer(
                None, 'email_cancel_order_customer', [args.get('email')], args)
    except:
        frappe.log_error(frappe.get_traceback(),
                         "go1_cms.api.doc_events.send_mail_sale_order")


def get_args_order(doc):
    doc.reload()
    try:
        domain = get_domain()
        address = {}
        if doc.customer_address:
            address = frappe.db.get_value('Address', doc.customer_address, [
                'address_title', 'address_line1', 'email_id', 'phone'], as_dict=1)

        # args mail
        redirect_to = f'{domain}/tai-khoan?tag=my-orders'
        items = []
        for item in doc.items:
            items.append({
                'item_name': item.item_name,
                'qty': item.qty,
                'uom': item.uom,
                'rate': item.rate,
                'amount': item.amount,
            })

        args = {
            'time': doc.creation.strftime("%d/%m/%Y %H:%M:%S"),
            'order_code': doc.name,
            'order_status': ORDER_STATUS.get(doc.status, {}).get('label') or doc.status,
            'full_name': address.get('address_title', ''),
            'phone_number': address.get('phone', ''),
            'email': address.get('email_id', ''),
            'address': address.get('address_line1', ''),
            'redirect_to': redirect_to,
            'items': items,
            'grand_total': doc.grand_total,
        }
        args['redirect_to'] = redirect_to

        return args
    except Exception as ex:
        return {}
