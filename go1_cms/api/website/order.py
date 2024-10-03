import frappe
from frappe import _
from pypika import functions as fn
import math
from webshop.webshop.shopping_cart.cart import (
    decorate_quotation_doc
)


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
    print('===========================')
    print(q_data)
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
        order = frappe.get_doc("Sales Order", order_name)
        return decorate_quotation_doc(order)
    return {}
