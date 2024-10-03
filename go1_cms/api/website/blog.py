import frappe
from frappe import _
from pypika import functions as fn
import math


@frappe.whitelist(allow_guest=True)
def get_categories():
    categories = frappe.db.get_all('Mbw Blog Category', fields=[
        'category_title as label', 'category_title as value'], order_by='creation')
    categories.insert(0, {
        "label": "Tất cả",
        "value": "",
    })
    return {'data': categories}


@frappe.whitelist(allow_guest=True)
def get_blog_list(name_section, **kwargs):
    try:
        page_no = int(kwargs.get('page_no', 1)) - 1
    except:
        page_no = 0

    page_len = 9
    text_search = kwargs.get('text_search', '')
    blog_category = kwargs.get('blog_category', None)

    doc_section = frappe.db.get_value('Page Section', name_section, [
        'sort_field', 'no_of_records', 'category'], as_dict=1)
    sort_field = doc_section.sort_field if doc_section.sort_field else 'published_on'
    limit = doc_section.no_of_records if doc_section.no_of_records else page_len
    if blog_category == None:
        blog_category = doc_section.category

    offset = page_no*limit
    sort_by = frappe.qb.desc
    if kwargs.get('sort_by', 'desc').lower() == "asc":
        sort_by = frappe.qb.asc

    MbwBlogPost = frappe.qb.DocType('Mbw Blog Post')
    # get data
    m_query = (frappe.qb.from_(MbwBlogPost)).where(MbwBlogPost.published == 1)

    if text_search:
        m_query = m_query.where(
            MbwBlogPost.title.like('%' + text_search+'%'))

    if blog_category:
        m_query = m_query.where(
            MbwBlogPost.category == blog_category)

    q_data = m_query.select(MbwBlogPost.name, MbwBlogPost.blogger, MbwBlogPost.title, MbwBlogPost.blog_intro, MbwBlogPost.route, MbwBlogPost.published_on, MbwBlogPost.meta_image).offset(offset).limit(
        limit).orderby(MbwBlogPost[sort_field], order=sort_by).distinct()

    blogs = q_data.run(as_dict=True)
    for item in blogs:
        published_on = item.get('published_on')
        item['published_on'] = published_on.strftime(
            "%d-%m-%Y")

    q_count = m_query.select(
        fn.Count(MbwBlogPost.name).as_('total').distinct())
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
    return {'data': blogs, 'pagination': pagination}


@frappe.whitelist(allow_guest=True)
def get_recent_blog(name_section, **kwargs):
    MbwBlogPost = frappe.qb.DocType('Mbw Blog Post')
    blog_category = kwargs.get('blog_category', None)

    doc_section = frappe.db.get_value('Page Section', name_section, [
        'sort_field', 'category'], as_dict=1)
    sort_field = doc_section.sort_field if doc_section.sort_field else 'published_on'
    if blog_category == None:
        blog_category = doc_section.category
    limit = kwargs.get('limit', '4')
    if limit.isdigit():
        limit = int(limit) if int(limit) <= 12 else 12
    else:
        limit = 4

    offset = 0
    sort_by = frappe.qb.desc

    m_query = (frappe.qb.from_(MbwBlogPost)).where(
        (MbwBlogPost.published == 1))
    if blog_category:
        m_query = m_query.where(
            MbwBlogPost.category == blog_category)

    q_data = m_query.select(MbwBlogPost.name, MbwBlogPost.blogger, MbwBlogPost.title, MbwBlogPost.blog_intro, MbwBlogPost.route, MbwBlogPost.published_on, MbwBlogPost.meta_image).offset(offset).limit(
        limit).orderby(MbwBlogPost[sort_field], order=sort_by)

    blogs = q_data.run(as_dict=True)
    for item in blogs:
        published_on = item.get('published_on')
        item['published_on'] = published_on.strftime(
            "%d-%m-%Y")

    return {'data': blogs}


@frappe.whitelist(allow_guest=True)
def get_related_blogs(name, **kwargs):
    related_blogs = []
    if frappe.db.exists("Mbw Blog Post", name):
        tags = frappe.db.get_all("MBW Blog Tag Item", filters={
                                 "parent": name, "parentfield": "tags"}, pluck="tag")
        name_blogs = [n for n in frappe.db.get_all("MBW Blog Tag Item", filters={
            "tag": ['in', tags], "parentfield": "tags"}, pluck="parent") or [] if n != name]

        name_section = kwargs.get('name_section', None)
        if name_section:
            doc_section = frappe.db.get_value('Page Section', name_section, [
                                              'no_of_records'], as_dict=1)
            limit = doc_section.no_of_records if doc_section.no_of_records else 3
        else:
            limit = kwargs.get('limit', '3')
            if limit.isdigit():
                limit = int(limit) if int(limit) <= 12 else 12
            else:
                limit = 3

        order_by = 'published_on desc'
        fields = ['published_on', 'name', 'title', 'blogger',
                  'route', 'blog_intro', 'meta_image']
        # related blogs
        related_filters = [['name', 'in', name_blogs], ['published', '=', 1], [
            'category', '=', frappe.db.get_value('Mbw Blog Post', name, 'category')]]
        related_blogs = frappe.get_all(
            "Mbw Blog Post",
            fields=fields,
            filters=related_filters,
            order_by=order_by,
            page_length=limit,
        ) or []

        for item in related_blogs:
            published_on = item.get('published_on')
            item['published_on'] = published_on.strftime(
                "%d-%m-%Y")

    return {'data': related_blogs}
