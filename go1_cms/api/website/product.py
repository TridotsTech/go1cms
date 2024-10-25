import frappe
from frappe import _, local
from frappe.utils import cint
from pypika import functions as fn

import json
import math

from webshop.webshop.product_data_engine.filters import ProductFiltersBuilder
# from webshop.webshop.product_data_engine.query import ProductQuery
from webshop.webshop.doctype.override_doctype.item_group import get_child_groups_for_website

from go1_cms.go1_cms.product_data_engine.query import ProductQuery


@frappe.whitelist(allow_guest=True)
def get_filter_product():
    filters = {}
    filter_engine = ProductFiltersBuilder()
    field_filters = []
    if filter_engine.get_field_filters():
        for i in filter_engine.get_field_filters():
            field_filters.append({
                'key': i[0].fieldname,
                'label': i[0].label,
                'values': i[1]
            })
    attribute_filters = []
    if filter_engine.get_attribute_filters():
        for i in filter_engine.get_attribute_filters():
            attribute_filters.append({
                'key': i.name,
                'label': i.name,
                'values': i.item_attribute_values
            })

    filters['field_filters'] = field_filters
    filters['attribute_filters'] = attribute_filters
    return filters


@frappe.whitelist(allow_guest=True)
def get_product_filter_data(**kwargs):
    limit = None
    sort_field = None
    sort_by = 'desc'
    order_by = None

    if kwargs:
        name_section = kwargs.get('name_section')
        if kwargs.get('sort_field') in ['creation', 'ranking']:
            sort_field = kwargs.get('sort_field')
        if frappe.db.exists('Page Section', name_section):
            doc_section = frappe.get_doc('Page Section', name_section)
            if not sort_field:
                sort_field = doc_section.sort_field
            limit = doc_section.no_of_records if doc_section.no_of_records else None
        if kwargs.get('sort_by', 'desc').lower() == "asc":
            sort_by = 'asc'

        query_args = frappe._dict(kwargs)

        text_search = query_args.get("text_search")
        field_filters = query_args.get("field_filters", {})
        if isinstance(field_filters, str):
            field_filters = json.loads(field_filters)
        attribute_filters = query_args.get("attribute_filters", {})
        if isinstance(attribute_filters, str):
            attribute_filters = json.loads(attribute_filters)
        page_no = cint(query_args.page_no) - \
            1 if query_args.get("page_no") else 0
        item_group = query_args.get("item_group")
        from_filters = query_args.get("from_filters")
    else:
        text_search, attribute_filters, item_group, from_filters = None, None, None, None
        field_filters = {}
        page_no = 0

    # order_by
    if sort_by and sort_field:
        order_by = f"{sort_field} {sort_by}"

    # if new filter is checked, reset page_no to show filtered items from page 1
    if from_filters:
        page_no = 0

    sub_categories = []
    if item_group:
        sub_categories = get_child_groups_for_website(
            item_group, immediate=True)

    page_length = limit or 0
    engine = ProductQuery()

    try:
        result = engine.query(
            attribute_filters,
            field_filters,
            search_term=text_search,
            start=page_no*page_length,
            page_length=page_length,
            item_group=item_group,
            order_by=order_by
        )
    except Exception:
        frappe.log_error("Product query with filter failed")
        return {"exc": "Something went wrong!"}

    # discount filter data
    filters = {}
    discounts = result["discounts"]

    if discounts:
        filter_engine = ProductFiltersBuilder()
        filters["discount_filters"] = filter_engine.get_discount_filters(
            discounts)

    items_count = result["items_count"]
    if items_count and page_length > 0:
        total_page = math.ceil(items_count/page_length)
    else:
        total_page = 0

    pagination = {
        'current_page': page_no + 1,
        'total': items_count,
        'total_page': total_page,
        'limit': page_length,
    }

    return {
        "data": result["items"] or [],
        "pagination": pagination,
    }
