import frappe
from frappe import _
from pypika import functions as fn
import math
from webshop.webshop.shopping_cart.cart import (
    decorate_quotation_doc
)

LST_STATUS = [
    {"label": "Tất cả", "value": ""},
    {"label": "Chờ xử lý", "value": "Draft"},
    {"label": "Chờ giao hàng và thanh toán", "value": "To Deliver and Bill"},
    {"label": "Chờ thanh toán", "value": "To Bill"},
    {"label": "Chờ giao hàng", "value": "To Deliver"},
    {"label": "Hoàn thành", "value": "Completed"},
    {"label": "Đã hủy", "value": "Cancelled"},
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

    page_len = 9
    text_search = kwargs.get('text_search', '')
    status = kwargs.get('status', None)
    time_start = kwargs.get('time_start', None)
    time_end = kwargs.get('time_end', None)

    doc_section = frappe.db.get_value('Page Section', name_section, [
        'no_of_records'], as_dict=1)
    sort_field = 'transaction_date'
    limit = doc_section.no_of_records if doc_section.no_of_records else page_len

    offset = page_no*limit
    sort_by = frappe.qb.desc
    if kwargs.get('sort_by', 'desc').lower() == "asc":
        sort_by = frappe.qb.asc

    SalesOrder = frappe.qb.DocType('Sales Order')
    # get data
    m_query = (frappe.qb.from_(SalesOrder))
    if text_search:
        m_query = m_query.where(
            SalesOrder.name.like('%' + text_search+'%'))
    if status:
        m_query = m_query.where(
            SalesOrder.status == status)

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
            "%d-%m-%Y")

    q_count = m_query.select(
        fn.Count(SalesOrder.name).as_('total').distinct())
    rs_count = q_count.run(as_dict=True)
    if rs_count and limit > 0:
        total_page = math.ceil(rs_count[0].total/limit)
    else:
        total_page = 0

    pagination = {
        'current_page': page_no + 1,
        'total': rs_count[0].total if rs_count and limit > 0 else 0,
        'total_page': total_page,
        'limit': limit,
    }
    return {'data': qts, 'pagination': pagination}


@frappe.whitelist(methods=['GET'])
def get_detail_order(order_name):
    if frappe.db.exists("Sales Order", order_name):
        order = frappe.get_doc("Sales Order", order_name).as_dict()
        transaction_date = order.get('transaction_date')
        order['transaction_date'] = transaction_date.strftime(
            "%d-%m-%Y")
        stat = next((item for item in LST_STATUS if item["value"] == order['status']), None)
        if stat:
            order['status'] = stat.get('label')
        
        address_billing_info = {}
        if order.customer_address:
            address_billing_info = frappe.db.get_value("Address", order.customer_address, ['address_title as full_name', 'email_id as email', 'phone', 'address_line1 as address'],as_dict=1)
        order['address_billing_info'] = address_billing_info
            
        return order
    return {}
