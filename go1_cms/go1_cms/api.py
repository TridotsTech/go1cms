# -*- coding: utf-8 -*-
# Copyright (c) 2019, Tridots and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import os
import re
import json
import mimetypes
from frappe.utils import getdate, nowdate, now, get_url

TEMPLATE_HEADER = {
    'Template 1': 'header.html',
    'Template 2': 'header.html',
    'Template 3': 'header.html',
    'Template 4': 'header.html',
}


@frappe.whitelist(allow_guest=True)
def get_template_folder(url=None, business=None, temp=0):
    try:
        if not url:
            path = frappe.get_module_path("go1_cms")
            path_parts = path.split('/')
            path_parts = path_parts[:-1]
            url = '/'.join(path_parts)
        if business:
            if not os.path.exists(os.path.join(url, 'templates/pages', business)):
                frappe.create_folder(os.path.join(
                    url, 'templates/pages', business))
            temp_path = os.path.join(url, 'templates/pages', business)
            if temp == 1:
                temp_path = os.path.join('templates/pages', business)
        else:
            if not os.path.exists(os.path.join(url, 'templates/pages', 'custom_html')):
                frappe.create_folder(os.path.join(
                    url, 'templates/pages', 'custom_html'))
            temp_path = os.path.join(url, 'templates/pages', 'custom_html')
            if temp == 1:
                temp_path = os.path.join('templates/pages', 'custom_html')
        return temp_path
    except Exception:
        frappe.log_error(frappe.get_traceback(), _("api.get_template_folder"))


@frappe.whitelist()
def unescape(s):
    try:
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        # this has to be last:
        s = s.replace("&amp;", "&")
        return s
    except Exception:
        frappe.log_error(frappe.get_traceback(), "api.unescape")


@frappe.whitelist(allow_guest=True)
def get_scroll_content(route, page_no=0, page_len=3, device_type=None):
    business = None
    context = {}
    start = int(page_no) * int(page_len)
    page_builder = frappe.get_doc('Web Page Builder', {"route": route})
    page_section = frappe.get_all("Mobile Page Section", fields=["name", "section", "parent", "section_title"], filters={
                                  "parent": page_builder.name, 'parentfield': 'web_section'}, order_by='idx')
    page_section = page_section[start:int(page_len) + int(start)]
    page_template = ""
    catalog_settings = get_settings_from_domain('Catalog Settings')
    context['catalog_settings'] = catalog_settings
    context['general_settings'] = get_settings_from_domain('Business Setting')
    context['currency'] = frappe.cache().hget('currency', 'symbol')
    product_box = catalog_settings.product_boxes
    if product_box:
        context['product_box'] = frappe.db.get_value(
            'Product Box', product_box, 'route')
    for item in page_section:
        section_template = frappe.db.get_value("Page Section", item.section, [
                                               "name", "business", "section_title"], as_dict=True)
        if page_builder.business:
            business = page_builder.business
        temp_path = get_template_folder(business=business, temp=1)
        html_page = section_template.section_title.lower().replace(
            ' ', '-') + "-" + (section_template.name).lower().replace(' ', '-')
        data_source = get_section_data(item.section, item.parent, device_type)
        context[data_source['context']] = {}
        for key, value in data_source.items():
            context[data_source['context']][key] = value
        template = frappe.render_template(os.path.join(
            temp_path, (html_page+'.html')), context)
        page_template += template
    return page_template


@frappe.whitelist(allow_guest=True)
def get_section_data(section, page_builder, device_type):
    from go1_cms.go1_cms.doctype.web_page_builder.web_page_builder import get_source_doc_data, get_page_section
    page_builder = frappe.get_doc('Web Page Builder', page_builder)
    source_doc, sections = get_source_doc_data(page_builder, device_type)
    # frappe.log_error(source_doc,"source_doc")
    # frappe.log_error(sections,"sections")
    data = get_page_section(source_doc)
    doc = frappe.get_doc("Page Section", section)
    data_source = next((x for x in data if x.get('section') == section), None)
    return data_source


def resolve_from_map(path):
    m = Map([Rule(r["from_route"], endpoint=r["to_route"], defaults=r.get("defaults"))
            for r in get_website_rules()])

    if frappe.local.request:
        urls = m.bind_to_environ(frappe.local.request.environ)
    try:
        endpoint, args = urls.match("/" + path)
        path = endpoint
        if args:
            frappe.local.no_cache = 1
            frappe.local.form_dict.update(args)

    except NotFound:
        pass

    return path


def get_website_rules():
    '''Get website route rules from hooks and DocType route'''
    def _get():
        rules = frappe.get_hooks("website_route_rules")
        for d in frappe.get_all('DocType', 'name, route', dict(has_web_view=1)):
            if d.route:
                rules.append(
                    dict(from_route='/' + d.route.strip('/'), to_route=d.name))
        for p in frappe.get_all('Web Page Builder', 'name, route', dict(published=1)):
            if p.route:
                html_page = p.route.lower().replace('-', '_')
                rules.append(dict(from_route='/' + html_page,
                             to_route=p.route.strip('/')))
        return rules
    return _get()


@frappe.whitelist(allow_guest=True)
def shipping_zip_matches(zip):
    zipcoderanges = []
    returnValue = False
    zip_location = ''
    zip_ranges = frappe.db.get_all('Zipcode Range', fields=['*'])
    if zip_ranges:
        for zip_code in zip_ranges:
            if zip_code.zipcode_range:
                if zip_code.zipcode_range.find(',') > -1:
                    zipcoderanges = zip_code.zipcode_range.split(',')
                    for x in zipcoderanges:
                        if x.find('-') > -1:
                            zipcoderanges_after = x.split('-')
                            for zipcode in range(int(zipcoderanges_after[0]), int(zipcoderanges_after[1]) + 1):
                                if str(zipcode).lower() == str(zip).lower():
                                    returnValue = True
                                    zip_location = zip_code.zipcode_for
                        else:
                            if str(x).lower().replace(" ", "") == str(zip).lower().replace(" ", ""):
                                returnValue = True
                                zip_location = zip_code.zipcode_for
                elif zip_code.zipcode_range.find('-') > -1:
                    zipcoderanges_after = ziprange.split('-')
                    for zipcode in range(int(zipcoderanges_after[0]), int(zipcoderanges_after[1]) + 1):
                        if str(zipcode).lower() == str(zip).lower():
                            returnValue = True
                            zip_location = zip_code.zipcode_for
                else:
                    if str(zip_code.zipcode_range).lower() == str(zip).lower():
                        returnValue = True
                        zip_location = zip_code.zipcode_for
    return {'returnValue': returnValue, 'zip_location': zip_location}


@frappe.whitelist()
def get_section_layouts():
    return frappe.db.sql('''select name, web_layout, tab_layout, mobile_layout from `tabLayout`''', as_dict=1)


@frappe.whitelist()
def get_section_components():
    components = frappe.db.sql(
        '''select name, html from `tabSection Component` order by name''', as_dict=1)
    for item in components:
        item.content = frappe.db.sql('''select group_name, field_label, field_key, field_type, content_type, content, fields_json from `tabSection Content` where parent = %(parent)s and parenttype = "Section Component" order by idx''', {
                                     'parent': item.name}, as_dict=1)
    return components


@frappe.whitelist()
def get_styles_list():
    style_groups = frappe.db.sql(
        '''select name from `tabCSS Group` order by name''', as_dict=1)
    for item in style_groups:
        item.style_elements = frappe.db.sql(
            '''select name, property_name, value_type, options_json from `tabCSS Property` where css_group = %(group)s order by name''', {'group': item.name}, as_dict=1)
    return style_groups


@frappe.whitelist(allow_guest=True)
def check_domain(domain_name):
    try:
        from frappe.core.doctype.domain_settings.domain_settings import get_active_domains
        domains_list = get_active_domains()
        domains = frappe.cache().hget('domains', 'domain_constants')
        # if not domains:
        # 	domains = get_domains_data()
        if not domains:
            return False
        if domains[domain_name] in domains_list:
            return True
        return False
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),
                         'go1_cms.go1_cms.api.check_domain')


@frappe.whitelist(allow_guest=True)
def get_business_from_login(abbr=None):
    business = None
    if 'Vendor' in frappe.get_roles(frappe.session.user) and frappe.session.user != 'Administrator':
        shop_user = frappe.db.get_all('Shop User',
                                      filters={'name': frappe.session.user},
                                      fields=['restaurant'])
        if shop_user and shop_user[0].restaurant:
            business = shop_user[0].restaurant
    return business


@frappe.whitelist(allow_guest=True)
def get_today_date(time_zone=None, replace=False):
    '''
            get today  date based on selected time_zone
    '''

    if not time_zone:
        time_zone = frappe.db.get_single_value('System Settings', 'time_zone')
    currentdate = datetime.now()
    currentdatezone = datetime.now(timezone(time_zone))
    if replace:
        return currentdatezone.replace(tzinfo=None)
    else:
        return currentdatezone


@frappe.whitelist(allow_guest=True)
def get_page_content(route=None, user=None, customer=None, domain=None, business=None, application_type="mobile"):
    '''
            To get dynamic page information

            param: route: get page based on route. For home page no need to send any route value
            param: user: user id (optional).
            param: customer: customer id (optional). This is required for fetching login based records
            param: domain: get domain based records
    '''
    # updated by boopathy

    # if route and application_type:
    # 	home = frappe.db.get_all('Web Page Builder', filters={'route': route}, fields=['name', 'page_type'])
    # 	return get_page_builder_data(home,application_type)
    # end by boopathy
    page_content = page_type = list_content = list_style = detail_content = None
    side_menu = sub_header = None
    if user and not customer:
        customer_info = frappe.db.get_all(
            'Customers', filters={'user_id': user})
        if customer_info:
            customer = customer_info[0].name
    if business:
        home = frappe.db.get_all('Web Page Builder', filters={
                                 'business': business}, fields=['name', 'page_type'])
        if home:
            page_content = get_page_builder_data(
                home, customer, application_type, business=business)
    if not check_domain("multi_store"):
        business = None
    if domain and not route:

        # removed product_box from Website get_list-by sivaranjani
        check_website = frappe.db.get_all('Website', filters={
                                          'domain_name': domain}, fields=['business', 'theme', 'home_page'])
        if check_website and check_website[0].home_page:
            # changed filter from 'name': to 'route':  get_list-by sivaranjani
            home = frappe.db.get_all('Web Page Builder', filters={
                                     'route': check_website[0].home_page}, fields=['name', 'page_type'])
            if home:
                page_content = get_page_builder_data(
                    home, customer, business=business)
    if not route and not domain:
        home_page = frappe.db.get_single_value('Website Settings', 'home_page')
        home = frappe.db.get_all('Web Page Builder', filters={
                                 'route': home_page}, fields=['name', 'page_type'])
        if home:
            page_content = get_page_builder_data(
                home, customer, application_type, business=business)
    else:

        if check_domain("saas"):
            business = get_business_from_web_domain(domain)
        filters = [['route', '=', route]]
        if business:
            if not check_domain("multi_store"):
                filters.append(['business', '=', business])
        check_builder = frappe.db.get_all('Web Page Builder', filters=filters, fields=[
                                          'name', 'page_type', 'w_page_type'])

        if check_builder:
            page_type = check_builder[0].w_page_type
            if check_builder[0].page_type != "List" and check_builder[0].page_type != "Detail":
                page_content = get_page_builder_data(
                    check_builder, customer, application_type, business=business)
        else:
            check_section = frappe.db.get_all(
                'Page Section', filters=filters, fields=['name'])
            if check_section:
                from ecommerce_business_store.cms.doctype.page_section.page_section import get_section_data
                page_content = get_section_data(
                    check_section[0].name, customer)
    if page_type == "List":
        list_content = []
        check_builder = frappe.db.get_all('Web Page Builder', filters=filters, fields=['name', 'side_menu_display_field', 'side_menu_position', 'list_style',
                                          'page_type', 'list_style', 'columns_mapping', 'document', 'condition', 'sort_field', 'sort_by', 'enable_side_menu', 'data_fetch_from'])
        if check_builder:
            columns = ''
            condition = ''
            order_by = " ORDER BY creation DESC "
            if check_builder[0].condition:
                condition = " WHERE "+check_builder[0].condition
            if check_builder[0].sort_field:
                order_by = " ORDER BY " + \
                    check_builder[0].sort_field+" " + check_builder[0].sort_by
            cols_json = json.loads(check_builder[0].columns_mapping)
            for x in cols_json:
                for key in x.keys():
                    # frappe.log_error(key,'key')
                    columns += x[key]+" as "+key+","
            columns = columns[:-1]
            list_content = frappe.db.sql(""" SELECT {columns} FROM `tab{document}` doc {condition} {order_by}""".format(
                condition=condition, order_by=order_by, columns=columns, document=check_builder[0].document), as_dict=1)
            list_style = check_builder[0].list_style
            if check_builder[0].enable_side_menu:
                s_data = None
                if check_builder[0].data_fetch_from:
                    s_data = frappe.db.get_all(
                        check_builder[0].data_fetch_from, fields=['*'])
                side_menu = {"enabled": check_builder[0].enable_side_menu, "data": s_data,
                             'position': check_builder[0].side_menu_position, 'display_field': check_builder[0].side_menu_display_field}
            else:
                side_menu = {"enabled": 0}

    header_content = None
    footer_content = None
    if route:
        theme_settings = frappe.db.get_all("Web Theme", filters={"is_active": 1}, fields=[
                                           'default_header', 'default_footer', 'enable_page_title', 'page_title_bg', 'page_title_tag', 'title_text_align', 'page_title_overlay', 'page_title_color', 'container_max_width'])
        page_builder_dt = frappe.db.get_all('Web Page Builder', filters={'route': route}, fields=[
                                            'text_color', 'is_transparent_sub_header', 'sub_header_title', 'sub_header_bg_color', 'sub_header_bg_img', 'footer_component', 'header_component', 'enable_sub_header', 'edit_header_style', 'is_transparent_header'])
        if page_builder_dt:
            if page_builder_dt[0].footer_component:
                footer_content = get_footer_info(
                    page_builder_dt[0].footer_component)
            else:
                if theme_settings:
                    if theme_settings[0].default_footer:
                        footer_content = get_footer_info(
                            theme_settings[0].default_footer)

            if page_builder_dt[0].header_component:
                header_content = get_header_info(
                    page_builder_dt[0].header_component)

            else:
                if theme_settings:
                    if theme_settings[0].default_header:
                        header_content = get_header_info(
                            theme_settings[0].default_header)

            if page_builder_dt[0].enable_sub_header:
                sub_header = {"enabled": 1, "sub_header_title": page_builder_dt[0].sub_header_title,
                              "sub_header_bg_color": page_builder_dt[0].sub_header_bg_color,
                              "is_transparent": page_builder_dt[0].is_transparent_sub_header,
                              "text_color": page_builder_dt[0].text_color,
                              "container_max_width": page_builder_dt[0].container_max_width,
                              "enable_breadcrumbs": page_builder_dt[0].enable_breadcrumbs,
                              "page_title_overlay": page_builder_dt[0].page_title_overlay,
                              "sub_header_bg_img": page_builder_dt[0].sub_header_bg_img,
                              "title_text_align": page_builder_dt[0].title_text_align,
                              }
            else:
                sub_header = {"enabled": 0}
                if theme_settings:
                    if theme_settings[0].enable_page_title:
                        sub_header = {"enabled": 1,
                                      "sub_header_title": page_builder_dt[0].name,
                                      "sub_header_bg_color": theme_settings[0].page_title_bg,
                                      "sub_header_bg_img": theme_settings[0].page_title_bg_img,
                                      "is_transparent": theme_settings[0].is_transparent,
                                      "text_color": theme_settings[0].page_title_color,
                                      "page_title_overlay": theme_settings[0].page_title_overlay,
                                      "title_text_align": theme_settings[0].title_text_align,
                                      "container_max_width": theme_settings[0].container_max_width,
                                      "enable_breadcrumbs": theme_settings[0].enable_breadcrumbs,
                                      }

            if page_builder_dt[0].edit_header_style:
                if page_builder_dt[0].is_transparent_header:
                    header_content.is_transparent_header = 1

    return {"sub_header": sub_header, "side_menu": side_menu, "list_content": list_content, "list_style": list_style, "page_type": page_type, "page_content": page_content, "header_content": header_content, "footer_content": footer_content}


@frappe.whitelist(allow_guest=True)
def get_detail_page_content(route):
    check_dt = frappe.db.sql(
        """ select D.name from `tabDocType` D inner join  where has_web_view=1 """, as_dict=1)
    for x in check_dt:
        pass


@frappe.whitelist(allow_guest=True)
def get_page_side_menu_data(page_route, linked_doc, page_no=1, page_size=10):
    page_doc = frappe.db.get_all('Web Page Builder', filters={"route": page_route}, fields=[
                                 'columns_mapping', 'name', 'page_type', 'document', 'enable_side_menu', 'data_fetch_from', 'condition', 'sort_field', 'sort_by'])
    if page_doc:
        if page_doc[0].enable_side_menu == 1 and page_doc[0].data_fetch_from and page_doc[0].document:
            link_fields = frappe.db.sql(""" SELECT fieldname FROM `tabDocField` WHERE parent=%(dt)s AND options=%(linked_doc)s """, {
                                        "dt": page_doc[0].document, "linked_doc": page_doc[0].data_fetch_from}, as_dict=1)
            if link_fields:
                columns = ''
                condition = ' WHERE doc.{link_field} = "{linked_doc}"'.format(
                    link_field=link_fields[0].fieldname, linked_doc=linked_doc)
                order_by = " ORDER BY creation DESC "
                if page_doc[0].condition:
                    condition = " AND "+page_doc[0].condition
                if page_doc[0].sort_field:
                    order_by = " ORDER BY " + \
                        page_doc[0].sort_field+" " + page_doc[0].sort_by
                cols_json = json.loads(page_doc[0].columns_mapping)
                for x in cols_json:
                    for key in x.keys():
                        # frappe.log_error(key,'key')
                        columns += x[key]+" as "+key+","
                columns = columns[:-1]
                # frappe.log_error(columns,'columns')
                # frappe.log_error(condition,'condition')
                list_content = frappe.db.sql(""" SELECT {columns} FROM `tab{document}` doc {condition} {order_by} limit {page_no},{page_len} """.format(
                    condition=condition, order_by=order_by, columns=columns, document=page_doc[0].document, page_no=(int(page_no) - 1) * int(page_size), page_len=page_size), as_dict=1)
                return list_content
    return []


def get_page_builder_data(page, customer=None, application_type="mobile", business=None):
    # frappe.log_error(customer, "---customer--page-builder--")
    path = frappe.utils.get_files_path()
    import os
    if page[0].page_type == 'Adaptive':
        ptype = ('_web')
        if application_type == "mobile":
            ptype = ('_mobile')
    else:
        ptype = ('_web')
    use_page_builder = 1
    page_builders = frappe.db.get_all("Web Page Builder", filters={
                                      "name": page[0].name}, fields=['use_page_builder'])

    if page_builders:
        use_page_builder = page_builders[0].use_page_builder
    if use_page_builder:
        with open(os.path.join(path, 'data_source', (page[0].name.lower().replace(' ', '_') + ptype + '.json'))) as f:
            data = json.loads(f.read())
            from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
            lists = []
            # frappe.log_error(data, "---page_builders--")
            for item in data:
                # frappe.log_error(item, item.get('section'))
                if item.get('login_required') == 1 and customer:
                    doc = frappe.get_doc('Page Section', item.get('section'))
                    item['data'] = get_data_source(
                        doc.query, doc.reference_document, doc.no_of_records, 1, customer)
                if item.get('dynamic_data') == 1:

                    if item['section_type'] in ['Slider', 'Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
                        # frappe.log_error(item.get('section'), "---3--")
                        doc = frappe.get_doc(
                            'Page Section', item.get('section'))
                        doc.business = business
                        item = doc.run_method(
                            'section_data', customer=customer, add_info=None, store_business=business)

                # updated by boopathy-05.04.2022
                if item.get('section_type') == "Dynamic":
                    doc = frappe.get_list('Child Page Section', filters={"page_section": item.get('section')}, fields={"name", "conditions", "page_section", "section_type", "section_title",
                                          "reference_document", "sort_field", "sort_by", "custom_section_data", "is_editable", "dynamic_id", "field_list", "no_of_records", "background_color", "text_color"})
                    child_section_data = []
                    for d in doc:
                        sections = {}
                        sections['section_title'] = d['section_title']
                        sections['section_type'] = d['section_type']
                        if d['section_type'] == "Dynamic Section":
                            # frappe.log_error("calling")
                            query = "SELECT "
                            if not d['field_list']:
                                query += "* FROM `tab{reference_document}`"

                            if d['field_list'] and d['get_data_from_doctype'] == 0:
                                query += "{field_list} FROM `tab{reference_document}`"

                            if d['field_list'] and d['get_data_from_doctype'] == 1:
                                field_list = ""
                                fields = d['field_list'].split(',')
                                for i in fields:
                                    field_list += "B."+i+","
                                l = len(field_list)
                                field_list = field_list[:l-1]
                                query += "{field_list} FROM `tab{reference_document}` A "
                                # frappe.log_error(field_list,"field_list")

                            if d['get_data_from_doctype'] == 1 and d['reference_doc']:
                                query += "INNER JOIN `tab{from_doctype}` B ON A.name = B.{reference_field}"

                            if d['conditions']:
                                query += " WHERE {conditions}"
                            if d['reference_doc'] and d['get_data_from_doctype'] == 1 and not d['conditions']:
                                query += " WHERE A.name='{reference_doc}'"

                            if d['reference_doc'] and d['get_data_from_doctype'] == 1 and d['conditions']:
                                query += " and A.name='{reference_doc}'"

                            if d['reference_doc'] and d['get_data_from_doctype'] == 0 and d['conditions']:
                                query += "and parent={reference_doc}"

                            if d['reference_doc'] and d['get_data_from_doctype'] == 0 and not d['conditions']:
                                query += "WHERE parent={reference_doc}"

                            if d['sort_field'] and d['sort_by']:
                                query += " ORDER BY {sort_field} {sort_by} "
                            if d['no_of_records']:
                                query += " LIMIT {no_of_records} "

                            if d['get_data_from_doctype'] == 0:
                                res_data = frappe.db.sql(query.format(query=query, field_list=d['field_list'], reference_document=d['reference_document'], conditions=d['conditions'], sort_field=d['sort_field'], sort_by=d['sort_by'], no_of_records=d[
                                                         'no_of_records'], reference_doc=d['reference_doc'], get_data_from_doctype=d['get_data_from_doctype'], from_doctype=d['from_doctype'], reference_field=d['reference_field']), as_dict=1)
                            if d['get_data_from_doctype'] == 1:
                                res_data = frappe.db.sql(query.format(query=query, field_list=field_list, reference_document=d['reference_document'], conditions=d['conditions'], sort_field=d['sort_field'], sort_by=d['sort_by'], no_of_records=d[
                                                         'no_of_records'], reference_doc=d['reference_doc'], get_data_from_doctype=d['get_data_from_doctype'], from_doctype=d['from_doctype'], reference_field=d['reference_field']), as_dict=1)
                            sections['data'] = res_data
                            # frappe.log_error(res_data)

                            # frappe.log_error(custom_section_data,"custom section data")
                        child_section_data.append(sections)
                    item['child_section_data'] = child_section_data

                    # updated by boopathy
                lists.append(item)
            return lists
    else:
        return frappe.db.get_all("Web Page Builder", filters={"name": page[0].name}, fields=['content', 'name', 'use_page_builder'])

# def get_header_info(header_id):
# 	default_header = None
# 	headers_list = frappe.db.get_all("Header Component",filters={"name":header_id},fields=['menu','enable_top_menu','enable_search_bar','enable_cart','enable_wishlist','enable_account_menu','is_menu_full_width','layout_json'])
# 	if headers_list:
# 		menu = frappe.db.get_all("Menu",filters={"name":headers_list[0].menu},fields=['is_static_menu','name'])
# 		if menu:
# 			headers_list[0].is_static_menu = menu[0].is_static_menu
# 			parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":menu[0].name},as_dict=1)
# 			for x in parent_menus:
# 			 	x.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":x.menu_label,"menu_id":menu[0].name},as_dict=1)
# 			 	for sub_menu in x.child_menu:
# 			 		sub_menu.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":sub_menu.menu_label,"menu_id":menu[0].name},as_dict=1)
# 			headers_list[0].menus = parent_menus
# 			if headers_list[0].enable_top_menu==1:
# 				left_items =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":header_id},as_dict=1)
# 				for x in left_items:
# 				 	x.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":x.menu_label,"menu_id":header_id},as_dict=1)
# 				 	for sub_menu in x.child_menu:
# 				 		sub_menu.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":sub_menu.menu_label,"menu_id":header_id},as_dict=1)
# 				right_items =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":header_id},as_dict=1)
# 				for x in right_items:
# 				 	x.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":x.menu_label,"menu_id":header_id},as_dict=1)
# 				 	for sub_menu in x.child_menu:
# 				 		sub_menu.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":sub_menu.menu_label,"menu_id":header_id},as_dict=1)
# 				headers_list[0].top_menu = {"left_items":left_items,"right_items":right_items}
# 		default_header = headers_list[0]
# 	return default_header


def get_header_info(header_id):
    header_list = frappe.db.get_all("Header Component", filters={"name": header_id}, fields=[
        'is_transparent_header', 'title', 'is_menu_full_width', 'layout_json', 'enable_top_menu', 'sticky_on_top', 'is_dismissable', 'layout', 'sticky_header', 'call_to_action_button',  'is_transparent_header', 'sticky_header_background', 'menu_text_color', 'template_header', 'active_button', 'button_text', 'sub_text', 'icon_button', 'show_btn_text', 'show_sub_text', 'show_icon_btn', 'button_link', 'link_target', 'use_action', 'active_button_2', 'button_text_2', 'sub_text_2', 'icon_button_2', 'show_btn_text_2', 'show_sub_text_2', 'show_icon_btn_2', 'button_link_2', 'link_target_2', 'use_action_2', 'active_button_3', 'button_text_3', 'sub_text_3', 'icon_button_3', 'show_btn_text_3', 'show_sub_text_3', 'show_icon_btn_3', 'button_link_3', 'link_target_3', 'use_action_3', 'active_button_4', 'button_text_4', 'sub_text_4', 'icon_button_4', 'show_btn_text_4', 'show_sub_text_4', 'show_icon_btn_4', 'button_link_4', 'link_target_4', 'use_action_4', 'menu_item_spacing'
    ])
    if header_list:
        path = frappe.utils.get_files_path()
        if os.path.exists(os.path.join(path, 'data_source', (header_id.lower().replace(' ', '_') + '_web.json'))):
            lists = []
            with open(os.path.join(path, 'data_source', (header_id.lower().replace(' ', '_') + '_web.json'))) as f:
                data = json.loads(f.read())
                from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
                for item in data:
                    if item.get('section_type') == "Menu":
                        page_st = frappe.get_value(
                            "Page Section", item.get('section'), ['menu', 'custom_css'], as_dict=1)
                        item["custom_css"] = page_st['custom_css']
                        page_section_menu = page_st['menu']
                        menu = frappe.db.get_all("Menu", filters={"name": page_section_menu}, fields=[
                                                 'is_static_menu', 'name'])
                        if menu:
                            parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url,is_mega_menu,no_of_column,menu_id FROM `tabMenus Item` WHERE parent=%(menu_id)s AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""", {
                                                         "menu_id": menu[0].name}, as_dict=1)
                            # parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":menu[0].name},as_dict=1)
                            for x in parent_menus:
                                x.child_menu = frappe.db.sql(""" SELECT menu_label,redirect_url,icon,mega_m_col_index,menu_id FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND parent_menu=%(parent_menu)s ORDER BY idx""", {
                                                             "parent_menu": x.menu_id, "menu_id": menu[0].name}, as_dict=1)
                                for sub_menu in x.child_menu:
                                    sub_menu.child_menu = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND parent_menu=%(parent_menu)s ORDER BY idx""", {
                                                                        "parent_menu": sub_menu.menu_id, "menu_id": menu[0].name}, as_dict=1)
                            item["menus"] = parent_menus
                    lists.append(item)
            if lists:
                header_list[0].items = sorted(
                    lists, key=lambda d: d['column_index'])
            else:
                header_list[0].items = []
            if header_list[0].enable_top_menu == 1:
                left_items = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""", {
                                           "menu_id": header_id}, as_dict=1)
                for x in left_items:
                    x.child_menu = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""", {
                                                 "parent_menu": x.menu_label, "menu_id": header_id}, as_dict=1)
                    for sub_menu in x.child_menu:
                        sub_menu.child_menu = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""", {
                                                            "parent_menu": sub_menu.menu_label, "menu_id": header_id}, as_dict=1)
                right_items = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""", {
                                            "menu_id": header_id}, as_dict=1)
                for x in right_items:
                    x.child_menu = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""", {
                                                 "parent_menu": x.menu_label, "menu_id": header_id}, as_dict=1)
                    for sub_menu in x.child_menu:
                        sub_menu.child_menu = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""", {
                                                            "parent_menu": sub_menu.menu_label, "menu_id": header_id}, as_dict=1)
                header_list[0].top_menu = {
                    "left_items": left_items, "right_items": right_items}
        return header_list[0]
    return None


def get_footer_info(footer_id):
    footer_list = frappe.db.get_all("Footer Component", filters={"name": footer_id}, fields=[
                                    'title', 'enable_link_icon', 'layout_json', 'enable_copyright', 'copyright_layout', 'fc_ct_type', 'cp_fc_alignment', 'sc_ct_type', 'cp_sc_alignment', 'cp_fc_content', 'cp_sc_content', 'active_border_top'])
    if footer_list:
        path = frappe.utils.get_files_path()
        with open(os.path.join(path, 'data_source', (footer_id.lower().replace(' ', '_') + '_web.json'))) as f:
            data = json.loads(f.read())
            from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
            lists = []
            for item in data:
                if item.get('section_type') == "Menu":
                    page_section_menu = frappe.get_value(
                        "Page Section", item.get('section'), "menu")
                    menu = frappe.db.get_all("Menu", filters={"name": page_section_menu}, fields=[
                                             'is_static_menu', 'name'])
                    if menu:
                        parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url FROM `tabMenus Item` WHERE parent=%(menu_id)s AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""", {
                                                     "menu_id": menu[0].name}, as_dict=1)
                        item["menus"] = parent_menus
                lists.append(item)
        # sort INFO data by 'company' key.
        g_list = []
        column_indexes = frappe.db.sql("""SELECT column_index FROM `tabMobile Page Section` WHERE parent=%(f_id)s GROUP BY column_index""", {
                                       "f_id": footer_id}, as_dict=1)

        for x in column_indexes:
            result = [m for m in lists if m.get(
                "column_index") == x.get("column_index")]
            # filter(lambda m: m.get("column_index") == x.get("column_index"), lists)
            g_list.append({"column_index": x.column_index, "items": result})
        footer_list[0].items = g_list
        # footer_list[0].g_list = g_list
        if footer_list[0].layout_json:
            footer_list[0].layout_json_data = json.loads(
                footer_list[0].layout_json)
        return footer_list[0]
    return None


def key_func(k):
    return k['column_index']


@frappe.whitelist(allow_guest=True)
def update_website_context(context):
    context.no_cache = 1
    try:
        if frappe.local.session.data.csrf_token:
            context.csrf_token = frappe.local.session.data.csrf_token
        else:
            context.csrf_token = ''
        # get theme
        if context.doc and context.doc.doctype == "Web Page Builder" and context.doc.web_client_id:
            cl_web = frappe.get_all(
                "MBW Client Website", filters={"name": context.doc.web_client_id}, fields=['web_theme'])
            if cl_web:
                theme_list = frappe.get_all(
                    "Web Theme", filters={"name": cl_web[0].web_theme}, fields=['*'])
        else:
            theme_list = frappe.get_all(
                "Web Theme", filters={"is_active": 1}, fields=['*'])
        if not theme_list:
            theme_list = frappe.get_all(
                "Web Theme", fields=['*'], order_by='creation desc')
        footer_template = {}
        default_header = default_footer = None
        context.theme_settings = None
        header_dict = {}
        if theme_list:
            # theme = frappe.get_doc('Web Theme',theme_list[0]['name'])
            if theme_list[0].default_header:
                default_header = get_header_info(theme_list[0].default_header)
            if theme_list[0].default_footer:
                default_footer = get_footer_info(theme_list[0].default_footer)
            # frappe.log_error(theme_list[0],">> update web site context <<")
            theme_list[0].social_links = frappe.db.get_all("Social Link", filters={
                                                           "parent": theme_list[0].name}, fields=['icon', 'social_type', 'link_url'])
            theme_list[0].js_list = frappe.db.get_all(
                "Js List", filters={"parent": theme_list[0].name}, fields=['js_file'])
            theme_list[0].css_list = frappe.db.get_all(
                "Css List", filters={"parent": theme_list[0].name}, fields=['css_file'])
            context.theme_settings = theme_list[0]
        if default_header:
            if default_header.layout_json:
                default_header.layout_json = json.loads(
                    default_header.layout_json)
        if default_footer:
            if default_footer.layout_json:
                default_footer.layout_json = json.loads(
                    default_footer.layout_json)
        context.header = default_header
        context.footer = default_footer
        context.layout_template = "/templates/Layouts/layout.html"
        context.page_url = get_url()
        if context.doc:
            if context.doc.doctype == "Web Page Builder":
                if context.doc.enable_sub_header:
                    context.theme_settings.enable_page_title = 1
                    context.theme_settings.page_title_bg = context.doc.sub_header_bg_color
                    context.theme_settings.page_title_color = context.doc.text_color
                    context.theme_settings.page_title_bg_img = context.doc.sub_header_bg_img
                    context.theme_settings.enable_breadcrumbs = context.doc.enable_breadcrumbs
                    context.theme_settings.sub_header_title = context.doc.page_title
                    context.theme_settings.is_transparent = context.doc.is_transparent_sub_header
                    context.theme_settings.title_text_align = context.doc.title_text_align
                    context.theme_settings.page_title_overlay = context.doc.page_title_overlay
                    context.theme_settings.container_max_width = context.doc.container_max_width
                    context.theme_settings.page_title_padding = context.doc.page_title_padding
                    context.theme_settings.title_text_transform = context.doc.title_text_transform
                    context.theme_settings.page_title_tag = context.doc.page_title_tag
                    context.theme_settings.bg_overlay_opacity = context.doc.bg_overlay_opacity
                    if context.doc.sub_header_title:
                        context.theme_settings.sub_header_title = context.doc.sub_header_title
                if context.doc.dis_web_theme_subheader:
                    context.theme_settings.enable_page_title = 0
                # frappe.log_error(context.doc.header_component,">>context.doc.header_component<<")
                if context.doc.header_component or context.doc.footer_component:
                    if context.doc.header_component:
                        default_header = get_header_info(
                            context.doc.header_component)
                        # frappe.log_error(default_header,">>default_header<<")
                        if default_header:
                            if default_header.layout_json:
                                default_header.layout_json = json.loads(
                                    default_header.layout_json)
                                context.header = default_header
                                # frappe.log_error(context.header,">>context.header<<")
                    if context.doc.footer_component:
                        default_footer = get_footer_info(
                            context.doc.footer_component)
                        if default_footer:
                            if default_footer.layout_json:
                                default_footer.layout_json = json.loads(
                                    default_footer.layout_json)
                                context.footer = default_footer
                context.p_route = context.doc.route
                if context.p_route and "/" in context.doc.route:
                    context.p_route = context.doc.route.split('/')[1]
                if context.doc.edit_header_style:
                    if context.header and context.doc.is_transparent_header:
                        context.header.is_transparent_header = 1
        footer_items = []
        if context.footer:
            for sec_item in context.footer.get('items'):
                d = sec_item.copy()
                items = []
                for m_sec_item in sec_item.get("items"):
                    if m_sec_item.get('section_name') == "Mbw Policy":
                        context.theme_settings.mbw_policy = m_sec_item.get(
                            'policy')
                    if m_sec_item.get('web_template'):
                        m_sec_item['web_template'] = frappe.render_template(
                            m_sec_item.get('web_template'), {'m_sec_item': m_sec_item, 'theme_settings': context.theme_settings, 'footer': context.footer})
                    if m_sec_item.get('section_name') not in ['Mbw Policy', 'Social Links']:
                        items.append(m_sec_item)
                d['items'] = items
                footer_items.append(d)
        context.footer_items = footer_items
        get_device_type(context)
        if context.header.template_header:
            context.template_header = f"/templates/header/{TEMPLATE_HEADER[context.header.template_header]}"
        else:
            context.template_header = "/templates/header/header.html"

        # frappe.log_error(context.header,">> context.header <<")
        # frappe.log_error(context,">> context data <<")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),
                         "go1_cms.go1_cms.api.update_website_context")


def get_device_type(context):
    try:
        from go1_cms.go1_cms.device_detect.detect import detect_mobile_browser
        from go1_cms.go1_cms.device_detect.utilities import get_user_agent
        ua = None
        try:
            req = frappe.local.request
            ua = get_user_agent(req)
        except:
            pass
        if ua:
            context.user_agent = ua
            if detect_mobile_browser(ua):
                if "iPad" in ua:
                    context.device_type = "Desktop"

                else:
                    context.device_type = "Mobile"
            else:
                context.device_type = "Desktop"
        else:
            context.device_type = "Desktop"
    except Exception as e:
        context.device_type = "Desktop"
        frappe.log_error(frappe.get_traceback(),
                         "go1_cms.go1_cms.api.get_device_type")


@frappe.whitelist(allow_guest=True)
def get_all_website_settings():
    # theme = frappe.get_doc("Theme Settings")
    theme_list = frappe.get_all(
        "Web Theme", filters={"is_active": 1}, fields=['*'])
    if not theme_list:
        theme_list = frappe.get_all(
            "Web Theme", fields=['*'], order_by='creation desc')

    footer_template = {}
    default_header = default_footer = None
    header_dict = {}
    if theme_list:
        theme = frappe.get_doc('Web Theme', theme_list[0]['name'])
        if theme.default_header:
            default_header = get_header_info(theme.default_header)
        if theme.default_footer:
            default_footer = get_footer_info(theme.default_footer)

        return {"header_template": default_header, "footer_template": default_footer, "theme_settings": theme}


@frappe.whitelist(allow_guest=True)
def get_testing_footer_template():
    theme = frappe.get_doc("Theme Settings")
    data = get_footer_template(theme.default_footer)
    doc = frappe.get_doc("Footer Component", theme.default_footer)
    footer_list = frappe.get_doc("Footer Component", theme.default_footer)
    source_doc, sections, html = get_source_doc(footer_list, "Desktop")
    add_info = None
    html_list, js_list = get_page_html(
        doc, sections, html, source_doc, "Desktop", add_info)
    return html_list, js_list


def get_page_html(doc, sections, html, source_doc, device_type, add_info=None, page_no=0, page_len=3):
    # hided by boopathy on 10/08/2022
    # from ecommerce_business_store.ecommerce_business_store.api import get_all_restaurant_data, check_restaurant_distance
    # end
    section_list = sections[int(page_no):int(page_len)]
    data = get_page_section(source_doc)
    html_list = []
    js_list = ''
    res = {}
    # hided by boopathy
    # if doc.is_location_based:
    # 	latitude, longitude, order_type, distance = None, None, None, 0
    # 	try:
    # 		check_cookie = frappe.request.cookies.get('geoLocation')
    # 		if check_cookie:
    # 			cookie_val = urllib.parse.unquote(check_cookie)
    # 			latitude, longitude = cookie_val.split(',')
    # 			latitude = float(latitude)
    # 			longitude = float(longitude)
    # 		order_type = frappe.request.cookies.get('order_type') or "Delivery"
    # 	except Exception as e:
    # 		latitude, longitude = None, None
    # 	if latitude and longitude:
    # 		res = check_restaurant_distance(latitude, longitude)
    # 	distance = get_settings_value_from_domain('Business Setting', 'nearby_distance')
    # end
    for item in section_list:
        section_html, css, js, reference_document = frappe.db.get_value(
            'Page Section', item.section, [html, 'custom_css', 'custom_js', 'reference_document'])
        if section_html:
            if css:
                if css.find('<style') == -1:
                    section_html += '<style>{0}</style>'.format(css)
                else:
                    section_html += '{0}'.format(css)
            if js:
                if js.find('<script') == -1:
                    if page_no == 0:
                        js_list += frappe.render_template(
                            '<script>{0}</script>'.format(js), item.as_dict())
                    else:
                        section_html += '<script>{0}</script>'.format(js)
                else:
                    if page_no == 0:
                        js_list += frappe.render_template(
                            '{0}'.format(js), item.as_dict())
                    else:
                        section_html += '{0}'.format(js)
        data_source = next(
            (x for x in data if x.get('section') == item.section), None)
        allow = True
        if data_source.get('dynamic_data') == 1:
            if data_source['section_type'] in ['Slider', 'Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
                pg_doc = frappe.get_doc('Page Section', data_source['section'])
                # data_source = pg_doc.run_method('section_data', {'add_info': add_info})
                data_source = pg_doc.section_data(add_info=add_info)
        if data_source.get('login_required') == 1:
            if frappe.session.user != 'Guest':
                # modified by boopathy on 10/08/22
                # from ecommerce_business_store.cms.doctype.page_section.page_section import get_data_source
                from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
                # end
                doc = frappe.get_doc('Page Section', item.section)
                data_source['data'] = get_data_source(
                    doc.query, doc.reference_document, doc.no_of_records, 1, business=doc.business)
            else:
                allow = False
        if check_domain('restaurant') and data_source['section_type'] == 'Predefined Section' and doc.is_location_based:
            check_nearby = False
            if data_source.get('check_location'):
                check_nearby = True
            data_source['data'] = get_all_restaurant_data(
                data_source['data'], distance, check_nearby, latitude, longitude, sid=res.get('sid'), order_type=order_type)
            data_source['order_type'] = order_type
        if allow:
            # customer_data = bind_customer_cart()
            # data_source["cart"] = customer_data.get("cart_items")
            # data_source["my_boxes"] = customer_data.get("my_boxes")
            # catalog_settings = get_settings_from_domain('Catalog Settings')
            # general_settings = get_settings_from_domain('Business Setting')
            # # theme_settings =  get_settings_from_domain('Web Theme')
            # # theme = get_theme_settings()
            # currency = frappe.cache().hget('currency', 'symbol')
            # data_source['catalog_settings'] = catalog_settings
            # # data_source['theme_settings'] = theme_settings
            # data_source['general_settings'] = general_settings
            # data_source['currency'] = currency
            data_source['device_type'] = device_type
            product_box = None
            if data_source['section_type'] == 'Custom Section' and data_source['reference_document'] == "Product Category":
                category_product_box = frappe.db.get_value(
                    "Product Category", data_source['reference_name'], "product_box_for_list_view")
                if category_product_box:
                    product_box = category_product_box
            if product_box:
                data_source['product_box'] = frappe.db.get_value(
                    'Product Box', product_box, 'route')
            try:
                template = frappe.render_template(section_html, data_source)
                html_list.append(
                    {'template': template, 'section': item.section})
            except Exception as e:
                frappe.log_error(frappe.get_traceback(
                ), "ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.get_page_html")
    return html_list, js_list


# def get_footer_info(footer_id):
# 	html_list = []
# 	js_list = ''
# 	footer_template = {}
# 	footer_list = frappe.get_doc("Footer Component",footer_id)
# 	source_doc, sections, html = get_source_doc(footer_list,"Desktop")
# 	add_info = None
# 	html_list, js_list = get_page_html(footer_list, sections, html, source_doc, "Desktop", add_info)
# 	footer_template['html_list']=html_list
# 	footer_template['js_list']=js_list
# 	return footer_template


def get_page_section(source_doc):
    data = []
    path = frappe.utils.get_files_path()
    file_path = os.path.join(path, source_doc)
    if os.path.exists(file_path):
        with open(file_path) as f:
            data = json.loads(f.read())
    # frappe.log_error(data,"data")
    return data


def get_source_doc(doc, device_type):
    source_doc = sections = html = None
    if device_type == 'Desktop':
        view_type = 'web'
        sections = doc.web_section
        html = 'web_template'
    elif device_type == 'Mobile':
        view_type = 'mobile'
        sections = doc.mobile_section if doc.page_type == 'Adaptive' else doc.web_section
        html = 'mobile_view_template' if doc.page_type == 'Adaptive' else 'web_template'
    if doc.page_type == 'Responsive':
        source_doc = 'data_source/{0}_web.json'.format(
            doc.name.lower().replace(' ', '_'))
    else:
        source_doc = 'data_source/{0}_{1}.json'.format(
            doc.name.lower().replace(' ', '_'), (view_type if view_type else None))

    return source_doc, sections, html


@frappe.whitelist(allow_guest=True)
def get_blog_list(category=None, page_no=1, page_size=12):
    condition = ""
    if category:
        condition = " AND blog_category = '%s' " % (category)
    bloglist_query = "SELECT name,title,thumbnail_image,blog_intro,published_on,route FROM `tabBlog Post` WHERE published = 1 %s ORDER BY published_on DESC  limit %s,%s" % (
        condition, (int(page_no) - 1) * int(page_size), page_size)
    return frappe.db.sql(bloglist_query, as_dict=1)


@frappe.whitelist(allow_guest=True)
def get_blog_categories():
    bloglist_query = "SELECT name,title,route FROM `tabBlog Category` WHERE published = 1 ORDER BY creation DESC "
    return frappe.db.sql(bloglist_query, as_dict=1)


@frappe.whitelist(allow_guest=True)
def get_blog_details(route):
    blog_details = frappe.db.get_all(
        "Blog Post", filters={"route": route}, fields=["*"])
    if blog_details:
        condition = " AND blog_category = '%s' " % (
            blog_details[0].blog_category)
        related_bloglist_query = "SELECT name,title,thumbnail_image,blog_intro,published_on,route FROM `tabBlog Post` WHERE published = 1 AND route<>'%s' %s ORDER BY published_on DESC  limit %s,%s" % (
            route, condition, 0, 6)
        related_bloglist = frappe.db.sql(related_bloglist_query, as_dict=1)
        comments = frappe.db.get_all("Blog Comments", filters={"blog_name": blog_details[0].name}, fields=[
                                     "name1", "email", "comments", "creation"], order_by="creation desc")
        return {"status": "success", "blog_details": blog_details[0], "related_bloglist": related_bloglist, "comments": comments}
    else:
        return {"status": "failed", "Message": "Not Found"}


@frappe.whitelist(allow_guest=True)
def insert_blog_comments(data):
    doc = data
    if isinstance(doc, string_types):
        doc = json.loads(doc)
    response = doc
    blog = frappe.new_doc('Blog Comments')
    blog.blog_name = response.get('blog')
    blog.name1 = response.get('user_name')
    blog.email = response.get('email')
    blog.comments = response.get('message')
    blog.save(ignore_permissions=True)
    return blog.__dict__


@frappe.whitelist()
def get_blogger_bloglist(customer_email):
    check_blogger = frappe.db.get_all(
        "Blogger", filters={"user": customer_email})
    blogger_id = None
    if check_blogger:
        blogger_id = check_blogger[0].name
    return frappe.db.get_all("Blog Post", filters={"blogger": blogger_id}, fields=['name', 'title', 'blog_category', 'published_on', 'route', 'published', 'thumbnail_image'])


@frappe.whitelist()
def generate_sections_json():
    sections = []
    secs = frappe.db.get_all(
        "Section Template", order_by="creation ASC", limit_page_length=1000)
    for x in secs:
        s_template = frappe.get_doc("Section Template", x.name)
        st_obj = s_template.as_dict()
        st_obj.creation = None
        st_obj.modified = None
        sections.append(st_obj)
    # frappe.log_error(sections,"sections")


@frappe.whitelist()
def update_web_themes(doc, method):
    frappe.enqueue(update_website_themes, queue='default', doc=doc)


def update_website_themes(doc):
    update_themes = 1
    # if (doc.doctype == "Header Component" or doc.doctype == "Footer Component") and doc.get('update_theme') == 0:
    # 	update_themes = 0
    if update_themes == 1:
        my_filter = {}
        if doc.doctype == "Header Component":
            my_filter['default_header'] = doc.name
        elif doc.doctype == "Footer Component":
            my_filter['default_footer'] = doc.name
        elif doc.doctype == "Web Page Builder":
            if doc.web_client_id:
                cl_web = frappe.get_all(
                    "MBW Client Website", filters={"name": doc.web_client_id}, fields=['web_theme'])
                if cl_web:
                    my_filter['name'] = cl_web[0].web_theme
            else:
                my_filter['is_active'] = 1

        themes = frappe.db.get_all(
            "Web Theme",
            filters=my_filter,
            fields=['name']
        )
        for x in themes:
            theme = frappe.get_doc("Web Theme", x.name)
            theme.save(ignore_permissions=True)
            theme.reload()
