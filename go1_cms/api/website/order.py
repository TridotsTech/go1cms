import frappe
from frappe import _
from pypika import functions as fn
import math
import json
from webshop.webshop.shopping_cart.cart import (
    decorate_quotation_doc
)
from go1_cms.api.website.cart import (
    get_customer
)
from go1_cms.api.common import (
    ORDER_STATUS
)

LST_STATUS = [
    {"label": "Tất cả", "value": ""},
    {"label": "Chờ xác nhận", "value": "Draft", 'color': '#919EAB'},
    {"label": "Chờ giao hàng",
        "value": "To Deliver and Bill", 'color': '#1877F2'},
    {"label": "Hoàn thành", "value": "Completed", 'color': '#118D57'},
    {"label": "Đã hủy", "value": "Cancelled", 'color': '#B71D18'},
]


@frappe.whitelist(methods=['GET'])
def get_status_order():
    lst_status = LST_STATUS
    return lst_status


@frappe.whitelist(methods=['GET'])
def get_list_order(name_section, **kwargs):
    try:
        page_no = int(kwargs.get('page_no', 1)) - 1
    except:
        page_no = 0

    page_len = 10
    text_search = kwargs.get('text_search', '')
    status = kwargs.get('status', None)
    time_start = kwargs.get('time_start', None)
    time_end = kwargs.get('time_end', None)

    doc_section = frappe.db.get_value('Page Section', name_section, [
        'no_of_records'], as_dict=1)
    sort_field = 'creation'
    limit = doc_section.no_of_records if doc_section.no_of_records else page_len

    offset = page_no*limit
    sort_by = frappe.qb.desc
    if kwargs.get('sort_by', 'desc').lower() == "asc":
        sort_by = frappe.qb.asc

    SalesOrder = frappe.qb.DocType('Sales Order')
    # get data
    customer = get_customer()
    m_query = (frappe.qb.from_(SalesOrder)).where(
        SalesOrder.customer == customer.name)
    if text_search:
        m_query = m_query.where(
            SalesOrder.name.like('%' + text_search+'%'))
    if status:
        if status == 'Draft':
            ls_sta = ['Draft', 'On Hold']
        elif status == 'To Deliver and Bill':
            ls_sta = ['To Deliver and Bill', 'To Bill', 'To Deliver']
        elif status == 'Completed':
            ls_sta = ['Completed', 'Closed']
        elif status == 'Cancelled':
            ls_sta = ['Cancelled']
        else:
            ls_sta = [status]

        m_query = m_query.where(
            SalesOrder.status.isin(ls_sta))

    if time_start:
        m_query = m_query.where(
            SalesOrder.transaction_date >= time_start)
    if time_end:
        m_query = m_query.where(
            SalesOrder.transaction_date <= time_end)

    q_data = m_query.select(SalesOrder.name, SalesOrder.transaction_date, SalesOrder.status, SalesOrder.grand_total).offset(offset).limit(
        limit).orderby(SalesOrder[sort_field], order=sort_by).distinct()

    qts = q_data.run(as_dict=True)
    for item in qts:
        transaction_date = item.get('transaction_date')
        item['transaction_date'] = transaction_date.strftime(
            "%d/%m/%Y")
        stat = ORDER_STATUS.get(item['status'], None)
        if stat:
            item['status'] = stat.get('label')
            item['color_status'] = stat.get('color')

    q_count = m_query.select(
        fn.Count(SalesOrder.name).as_('total').distinct())
    rs_count = q_count.run(as_dict=True)
    if rs_count and limit > 0:
        total_page = math.ceil(rs_count[0].total/limit)
    else:
        total_page = 0
    # count all without filter
    q_count_all = (frappe.qb.from_(SalesOrder)).where(
        SalesOrder.customer == customer.name).select(fn.Count(SalesOrder.name).as_('total').distinct())
    rs_count_all = q_count_all.run(as_dict=True)
    total_all = rs_count_all[0].total

    pagination = {
        'current_page': page_no + 1,
        'total': rs_count[0].total if rs_count and limit > 0 else 0,
        'total_page': total_page,
        'limit': limit,
        'total_all': total_all
    }
    return {'data': qts, 'pagination': pagination}


@frappe.whitelist(methods=['GET'])
def get_detail_order(order_name):
    customer = get_customer()
    if frappe.db.exists("Sales Order", {'name': order_name, 'customer': customer.name}):
        order = frappe.get_doc("Sales Order", order_name).as_dict()
        transaction_date = order.get('transaction_date')
        order['transaction_date'] = transaction_date.strftime(
            "%d/%m/%Y")

        show_btn_cancel = False
        if order.status in ['Draft', 'On Hold']:
            show_btn_cancel = True

        stat = ORDER_STATUS.get(order['status'], None)
        if stat:
            order['status'] = stat.get('label')
            order['color_status'] = stat.get('color')

        address_billing_info = {}
        if order.customer_address:
            address_billing_info = frappe.db.get_value("Address", order.customer_address, [
                                                       'address_title as full_name', 'email_id as email', 'phone', 'address_line1 as address'], as_dict=1)
        order['address_billing_info'] = address_billing_info
        order['show_btn_cancel'] = show_btn_cancel
        return order
    return {}


@frappe.whitelist(methods=['POST'])
def cancel_order(order_name):
    try:
        customer = get_customer()
        if frappe.db.exists("Sales Order", {'name': order_name, 'customer': customer.name}):
            order = frappe.get_doc("Sales Order", order_name)
            if order.status in ['Draft', 'On Hold']:
                order.cms_send_mail_delivery = 0
                order.flags.ignore_permissions = True
                if order.status == "Draft":
                    order.submit()
                    order.reload()
                order.cancel()
                return {'status': 1, 'msg': 'Hủy đơn hàng thành công'}

        return {'status': 0, 'msg': 'Không thể hủy đơn hàng này'}
    except Exception as ex:
        frappe.throw('Có lỗi xảy ra')


@frappe.whitelist(methods=['GET'])
def get_comment_order(order_name, **kwargs):
    customer = get_customer()
    if frappe.db.exists("Sales Order", {'name': order_name, 'customer': customer.name}):
        Comment = frappe.qb.DocType('Comment')
        try:
            page_no = int(kwargs.get('page_no', 1)) - 1
        except:
            page_no = 0
        limit = 10
        offset = page_no*limit

        m_query = (frappe.qb.from_(Comment))\
            .where(Comment.comment_type == "Comment")\
            .where(Comment.reference_doctype == "Sales Order")\
            .where(Comment.reference_name == order_name)\
            .where(Comment.owner == frappe.session.user)

        q_data = m_query.select(Comment.name, Comment.comment_email, Comment.content, Comment.creation).offset(offset).limit(
            limit).orderby(Comment.creation, order=frappe.qb.desc).distinct()

        cmts = q_data.run(as_dict=True)
        for item in cmts:
            creation = item.get('creation')
            item['creation'] = creation.strftime(
                "%d/%m/%Y %H:%M:%S")

        q_count = m_query.select(
            fn.Count(Comment.name).as_('total').distinct())
        rs_count = q_count.run(as_dict=True)
        if rs_count and limit > 0:
            total_page = math.ceil(rs_count[0].total/limit)
        else:
            total_page = 0

        pagination = {
            'current_page': page_no + 1,
            'total': rs_count[0].total if rs_count and limit > 0 else 0,
            'total_page': total_page,
            'limit': limit
        }
        return {'data': cmts, 'pagination': pagination}
    return {'data': [], 'pagination': {}}


@frappe.whitelist(methods=['POST'])
def add_comment_order(order_name, content=''):
    if not content:
        frappe.throw('Vui lòng nhập nội dung')
    if len(content) > 1000:
        content = content[0:1000]

    customer = get_customer()
    if frappe.db.exists("Sales Order", {'name': order_name, 'customer': customer.name}):
        order = frappe.get_doc("Sales Order", order_name)
        order.add_comment('Comment', text=content)

        return {'status': 1, 'msg': 'Thêm nhận xét thành công'}
    return {'status': 0, 'msg': 'Không thể thêm nhận xét'}


@frappe.whitelist(methods=['POST'])
def delete_comment_order(order_name, id_cmt):
    if frappe.db.exists("Comment", {"name": id_cmt, "reference_doctype": "Sales Order", "reference_name": order_name, "owner": frappe.session.user}):
        frappe.db.delete('Comment', {'name': id_cmt})

        return {'status': 1, 'msg': 'Xóa nhận xét thành công'}
    return {'status': 0, 'msg': 'Không thể xóa nhận xét'}


@frappe.whitelist(methods=['GET'])
def get_order_status_list(order_name):
    customer = get_customer()
    if frappe.db.exists("Sales Order", {'name': order_name, 'customer': customer.name}):
        creation = frappe.db.get_value('Sales Order', order_name, 'creation')
        creation = creation.strftime(
            "%d/%m/%Y %H:%M:%S")

        lst_st = frappe.db.get_all(
            'Version',
            filters={
                'ref_doctype': 'Sales Order',
                'docname': order_name
            },
            fields=['name', 'data', 'creation'],
            order_by="creation asc"
        )

        lst_st_pretty = [{
            'status': 'Chờ xác nhận',
            'color': '#919EAB',
            'description': f'Đơn hàng được khởi tạo.',
            'creation': creation
        }]
        for s in lst_st:
            data = json.loads(s.data)
            changed = data.get('changed')
            creation = s.get('creation')
            creation = creation.strftime(
                "%d/%m/%Y %H:%M:%S")
            if changed and type(changed) == list:
                for c in changed:
                    if c[0] == 'status':
                        stat1 = ORDER_STATUS.get(c[1], {})
                        stat2 = ORDER_STATUS.get(c[2], {})
                        label1 = stat1.get('label') or c[1]
                        label2 = stat2.get('label') or c[2]

                        lst_st_pretty.append({
                            'status': label2,
                            'color': stat2.get('color') or '#919EAB',
                            'description': f'Trạng thái đơn hàng đã thay đổi từ `{label1}` sang `{label2}`.',
                            'creation': creation
                        })

        return lst_st_pretty
    return []
