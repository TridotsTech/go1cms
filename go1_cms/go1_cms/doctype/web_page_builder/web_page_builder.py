# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import os
import urllib.parse
from frappe.utils import encode, get_files_path, getdate
from frappe.model.mapper import get_mapped_doc
from frappe.website.website_generator import WebsiteGenerator
from go1_cms.go1_cms.api import check_domain, get_business_from_login
from frappe.model.naming import make_autoname
from go1_cms.go1_cms.api import get_template_folder, unescape
from urllib.parse import urljoin, unquote, urlencode
from datetime import datetime


class WebPageBuilder(WebsiteGenerator):
    def autoname(self):
        if check_domain('saas'):
            naming_series = 'WPB-'
            if not self.business:
                self.business = get_business_from_login()
            if self.business:
                naming_series = '{0}{1}-'.format(
                    naming_series, frappe.db.get_value('Business', self.business, 'abbr'))
            self.name = make_autoname(naming_series + '.#####', doc=self)
        else:
            self.name = self.page_title

    def validate(self):
        # frappe.log_error(frappe.local.session.data.csrf_token,'token')
        if self.is_new():
            self.file_path = ""
        if self.web_section:
            self.construct_html('web', 'web_section')
        if self.mobile_section:
            self.construct_html('mobile', 'mobile_section')
        route_prefix = ""
        r_prefix = frappe.db.get_all("CMS Route", filters={
            "page_type": self.w_page_type, "parent": "CMS Settings"}, fields=['page_prefix'])

        if r_prefix and r_prefix[0].page_prefix:
            route_prefix = r_prefix[0].page_prefix + "/"
        if self.route_template:
            route_prefix += self.route_template
        else:
            route_prefix += self.scrub(self.page_title)
        self.route = route_prefix

        if not self.meta_title:
            self.meta_title = self.page_title
        if not self.meta_keywords:
            self.meta_keywords = self.page_title.replace(" ", ", ")
        if not self.meta_description:
            self.meta_description = "About: "+self.page_title

    def on_update(self):
        # by siva
        enable_generate_html = frappe.db.get_single_value(
            "CMS Settings", "generate_html")
        if enable_generate_html:
            page_template = generate_page_html(page=self.name, view_type='web')
            if page_template:
                temp_path = get_template_folder(business=self.business)
                html_page = self.route.lower().replace('-', '_')
                with open(os.path.join(temp_path, (html_page+'.html')), "w") as f:
                    f.write(page_template)
                template_path = get_template_folder(
                    business=self.business, temp=1)
                if not self.file_path:
                    frappe.db.set_value("Web Page Builder", self.name, "file_path", os.path.join(
                        template_path, (html_page+'.html')))
                    frappe.db.commit()
            if self.web_section:
                for item in self.web_section:
                    from go1_cms.go1_cms.doctype.page_section.page_section import generate_section_html
                    generate_section_html(item.section)
            if self.mobile_section:
                for item in self.mobile_section:
                    from go1_cms.go1_cms.doctype.page_section.page_section import generate_section_html
                    generate_section_html(item.section)

        # if self.web_section:
        # 	css_text=""
        # 	for d in self.web_section:
        # 		res = frappe.get_list("Page Section",filters={"name":d.section},fields={"css_text"})
        # 		# frappe.log_error(res,"res")
        # 		if res and res[0]['css_text']:css_text +=str(res[0]['css_text'])
        # 	import os
        # 	from frappe.utils import get_files_path
        # 	path = get_files_path()
        # 	with open(os.path.join(path,'test.css'), "w") as f:
        # 		content = css_text
        # 		f.write(content)
            # return {"status":"success","message":"completed successfully"}
        # frappe.enqueue("ecommerce_business_store.ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.generate_css_file")
        generate_css_file()

    def after_delete(self):
        # delete file json
        path = get_files_path()
        if self.web_section:
            file_path = os.path.join(
                path, 'data_source', (self.name.lower().replace(' ', '_') + '_web.json'))
            if os.path.exists(file_path):
                os.remove(file_path)
        if self.mobile_section:
            file_path = os.path.join(
                path, 'data_source', (self.name.lower().replace(' ', '_') + '_mobile.json'))
            if os.path.exists(file_path):
                os.remove(file_path)

        for item in self.web_section:
            frappe.delete_doc('Page Section', item.section)

    def construct_html(self, view_type, ref_field):
        result = self.get_json_data(ref_field)

        path = get_files_path()
        if not os.path.exists(os.path.join(path, 'data_source')):
            frappe.create_folder(os.path.join(path, 'data_source'))
        with open(os.path.join(path, 'data_source', (self.name.lower().replace(' ', '_') + '_' + view_type + '.json')), "w") as f:
            if view_type == "mobile":
                content = json.dumps(json.loads(
                    frappe.as_json(result)), separators=(',', ':'))
                # f.write(frappe.as_json(result))
                f.write(content)
            else:
                # f.write(frappe.as_json(result))
                content = json.dumps(json.loads(
                    frappe.as_json(result)), separators=(',', ':'))
                # f.write(frappe.as_json(result))
                f.write(content)
        # self.file_path = '/files/data_source/{}.json'.format(self.name.lower().replace(' ', '_'))

    def get_json_data(self, ref_field):
        results = []
        for item in self.as_dict()[ref_field]:
            doc = frappe.get_doc('Page Section', item.section)
            obj = doc.run_method('section_data')
            results.append(obj)
        return results

    def get_context(self, context):
        doc = None
        add_info = {}
        if frappe.form_dict:
            add_info = frappe.form_dict
        if check_domain('saas') and context.get('web_domain'):
            if self.business and self.business == context.web_domain.business:
                doc = self
            else:
                check_routes = frappe.db.get_all('Web Page Builder', filters={
                    'route': self.route, 'business': context.web_domain.business})
                if check_routes:
                    doc = frappe.get_doc(
                        'Web Page Builder', check_routes[0].name)
            if not doc:
                frappe.local.flags.redirect_location = '/404'
                raise frappe.Redirect
        if check_domain('multi_store'):
            multi_store_business = frappe.request.cookies.get('selected_store')
            if not multi_store_business:
                all_locations = frappe.db.get_all("Shipping City", fields=[
                    'business', 'core_city'], order_by="is_default desc", limit_page_length=5)
                if all_locations:
                    multi_store_business = all_locations[0].business
            else:
                multi_store_business = unquote(
                    frappe.request.cookies.get('selected_store'))
            if multi_store_business:
                if self.business:
                    check_routes = frappe.db.get_all('Web Page Builder', filters={
                        'business': multi_store_business, 'published': 1})
                    if check_routes:
                        doc = frappe.get_doc(
                            'Web Page Builder', check_routes[0].name)
        if not doc:
            doc = self
        if not context.get('device_type'):
            context.device_type = 'Desktop'
        source_doc, sections, html = get_source_doc(doc, context.device_type)
        html_list = []
        if check_domain('restaurant'):
            preferred_date = frappe.request.cookies.get('order_date')
            preferred_time = frappe.request.cookies.get('order_time')
            if not preferred_date and not preferred_time:
                # hided by boopathy
                # from ecommerce_business_store.ecommerce_business_store.api import get_today_date
                # end
                preferred_date = getdate(get_today_date(replace=True))
                preferred_time = 'ASAP'
            context.preferred_date = getdate(preferred_date)
            context.preferred_time = urllib.parse.unquote(preferred_time)
            preferred_time_format = frappe.request.cookies.get(
                'order_time_format')
            if preferred_time_format:
                if urllib.parse.unquote(preferred_time) == 'ASAP' and preferred_time_format != 'ASAP':
                    preferred_time_format = 'ASAP'
                    frappe.local.cookie_manager.set_cookie(
                        "order_time_format", urllib.parse.unquote(preferred_time_format))
                context.preferred_time_format = urllib.parse.unquote(
                    preferred_time_format)
            frappe.local.cookie_manager.set_cookie(
                "order_date", str(getdate(preferred_date)))
            frappe.local.cookie_manager.set_cookie(
                "order_time", urllib.parse.unquote(preferred_time))
        if source_doc:
            html_list, js_list = get_page_html(
                doc=doc, sections=sections, html=html, source_doc=source_doc, device_type=context.device_type, blog_name=context.blog_name, add_info=add_info)
        context.html_list = html_list
        context.js_list = js_list

        if doc.custom_js and doc.custom_js.find('<script') == -1:
            context.custom_js = '<script>{0}</script>'.format(doc.custom_js)
        if doc.custom_css and doc.custom_css.find('<style') == -1:
            context.custom_css = '<style>{0}</style>'.format(doc.custom_css)

        # if doc.header_template:
        # 	context['header_file'] = frappe.db.get_value('Header Template', doc.header_template, 'route')
        # if doc.footer_template:
        # 	context['footer_file'] = frappe.db.get_value('Footer Template', doc.footer_template, 'route')
        if doc.header_component:
            header = []
            h_comp = frappe.db.get_all("Header Component", filters={
                "name": doc.header_component}, fields=['*'])
            if h_comp:
                header_dict = {}
                nav_menu = frappe.db.get_all("Menus Item", filters={"parent": h_comp[0]['menu']}, fields={
                    "menu_label", "parent_menu", "redirect_url", "position", "icon"})
                top_menu = frappe.db.get_all("Menus Item", filters={"parent": doc.header_component}, fields={
                    "menu_label", "parent_menu", "redirect_url", "position", "icon"})
                if nav_menu:
                    header_dict['nav_menus'] = nav_menu[0]
                if top_menu:
                    header_dict['top_menus'] = top_menu[0]
                header.append(header_dict)
            context['header'] = header
        if doc.footer_component:
            footer_template = None
            footer = frappe.db.get_all("Footer Component Item", filters={
                "parent": doc.footer_component}, fields={"title", "section_type", "column_count", "menu"})
            if footer and len(footer) > 0:
                for z in footer:
                    footer_template[z['section_type']] = frappe.db.get_all("Menus Item", filters={"parent": z['menu']}, fields={
                        "menu_label", "parent_menu", "redirect_url", "position", "icon"})
            context['footer'] = footer_template

        # frappe.log_error(doc,"doc111")
        context.doc = doc
        # frappe.log_error(context.doc.name,"context.doc")
        if doc.meta_title:
            context.meta_title = doc.meta_title
        if doc.meta_description:
            context.meta_description = doc.meta_description
        if doc.meta_keywords:
            context.meta_keywords = doc.meta_keywords
        enable_generate_html = frappe.db.get_single_value(
            "CMS Settings", "generate_html")
        if enable_generate_html:
            # by siva
            page_no = 0
            page_len = 3
            # modified by boopathy
            # from ecommerce_business_store.cms.api import get_section_data
            from go1_cms.go1_cms.api import get_section_data
            # end
            page_builder = frappe.get_doc('Web Page Builder', self.name)
            page_sections = frappe.get_all("Mobile Page Section", fields=["name", "section", "parent"], filters={
                "parent": page_builder.name, 'parentfield': 'web_section'}, order_by='idx')
            context['section_len'] = len(page_sections)
            page_sections = page_sections[int(page_no):int(page_len)]
            for item in page_sections:
                data = get_section_data(
                    item.section, item.parent, context.device_type)
                if data:
                    # updated by boopathy
                    if data.get('context') != None:
                        context[data['context']] = {}
                        for key, value in data.items():
                            context[data['context']][key] = value
            context.template = self.file_path
        p_route = self.route
        if "/" in p_route:
            p_route = p_route.split("/")[1]
        context.p_route = p_route
        if frappe.local.session.data.csrf_token:
            context.csrf_token = frappe.local.session.data.csrf_token
        else:
            context.csrf_token = ''


def get_product_context(self, context):
    try:
        # hided by boopathy on 10/08/2022
        # from ecommerce_business_store.ecommerce_business_store.api import get_bestsellers,get_product_price,get_category_products,get_category_detail,get_enquiry_product_detail,get_customer_recently_viewed_products, get_product_other_info,get_parent_categorie
        # end
        product_brands = []
        product_attributes = []

        if self.status != 'Approved':
            frappe.local.flags.redirect_location = '/404'
            raise frappe.Redirect
        catalog_settings = context.catalog_settings
        brand_cond = ''
        business = None
        if context.get('web_domain') and context.web_domain.business:
            business = context.web_domain.business
            if not self.restaurant or self.restaurant != business:
                frappe.local.flags.redirect_location = '/404'
                raise frappe.Redirect
        if business:
            brand_cond = ' and b.business = "{0}"'.format(business)
        context.brands = frappe.db.sql('''select b.name, b.brand_name, b.brand_logo, b.route, b.warranty_information as warranty_info, b.description from `tabProduct Brand` b inner join `tabProduct Brand Mapping` pbm on b.name = pbm.brand where pbm.parent = %(parent)s {condition} group by b.name order by pbm.idx'''.format(
            condition=brand_cond), {'parent': self.name}, as_dict=1)
        self.get_product_reviews(context)
        productattributes = frappe.db.get_all('Product Attribute Mapping', fields=[
            "*"], filters={"parent": self.name}, order_by="display_order", limit_page_length=50)
        image = []
        video_list = []
        if self.product_images:
            for item in self.product_images:
                image.append({"original_image": item.product_image, "product_image": item.detail_image,
                              "detail_image": item.detail_image, "detail_thumbnail": item.detail_thumbnail})
        img = None
        if self.product_images:
            context.og_image = self.product_images[0].product_image
        path1 = frappe.local.request.path
        context.page_url = get_url() + path1
        attr_product_title = ''
        size_chart = ''
        size_chart_params = ''
        chart_name = ''
        size_charts = ''
        for attribute in productattributes:
            if attribute.size_chart:
                chart_name = attribute.size_chart
                size_charts = frappe.db.get_all('Size Chart', filters={
                    'name': attribute.size_chart}, fields=['size_chart_image', 'name'])
                size_chart = frappe.db.sql('''select TRIM(attribute_values) as attribute_values,chart_title,chart_value,name from `tabSize Chart Content` where parent=%(parent)s order by display_order''', {
                    'parent': attribute.size_chart}, as_dict=1)
                unique_sizes = list(set([x.chart_title for x in size_chart]))
                # unique_attr = list(set([x.attribute_values for x in size_chart]))
                unique_attr = []
                for uni in size_chart:
                    if uni.attribute_values not in unique_attr:
                        unique_attr.append(uni.attribute_values)
                size_chart_list = []
                for attr in unique_attr:
                    sizes_list = list(
                        filter(lambda x: x.attribute_values == attr, size_chart))
                    # sizes_list = sorted(sizes_list,key=lambda x:x.get('display_order'),reverse=False)
                    arr = {}
                    if sizes_list:
                        arr['attribute'] = attr
                        for sz in unique_sizes:
                            check = next(
                                (x for x in sizes_list if x.chart_title == sz), None)
                            if check:
                                arr[sz] = check.chart_value
                            else:
                                arr[sz] = ''
                        size_chart_list.append(arr)
                size_chart = size_chart_list
                size_chart_params = unique_sizes
            options = frappe.db.get_all("Product Attribute Option", fields=[
                '*'], filters={'parent': self.name, 'attribute': attribute.product_attribute, 'attribute_id': attribute.name}, order_by='display_order', limit_page_length=50)
            for op in options:
                if op.is_pre_selected == 1:
                    if op.product_title and op.product_title != '-':
                        attr_product_title = op.product_title
                if op.image_list:
                    images = json.loads(op.image_list)
                    if len(images) > 0:
                        images = sorted(images, key=lambda x: x.get(
                            'is_primary'), reverse=True)
                        op.image_attribute = images[0].get('thumbnail')
                        if op.is_pre_selected == 1:
                            image = []
                            for im in images:
                                image.append({'original_image': im.get('image'), 'detail_image': im.get(
                                    'detail_thumbnail'), 'detail_thumbnail': im.get('thumbnail')})
                if op.is_pre_selected == 1:
                    attribute_video = frappe.get_all('Product Attribute Option Video', filters={
                        "option_id": op.name}, fields=["youtube_video_id", "video_type"])
                    if attribute_video:
                        for video in attribute_video:
                            if video.youtube_video_id:
                                video_list.append(
                                    {'video_link': video.youtube_video_id, 'video_type': video.video_type})

            product_attributes.append({"attribute": attribute.product_attribute, "attribute_name": attribute.attribute, "is_required": attribute.is_required, "control_type": attribute.control_type,
                                       "attribute_chart": attribute.size_chart, "options": options, "size_charts": size_charts, 'size_chart': size_chart, 'size_chart_params': size_chart_params})
        context.product_title = attr_product_title
        context.attr_image = image
        context.sel_image = img
        image_position = ''
        if catalog_settings.product_thumbnail_image_position:
            context.image_position = catalog_settings.product_thumbnail_image_position
        context.catalog_settings = catalog_settings
        context.attributes = product_attributes
        context.type_of_category = get_enquiry_product_detail(self.name)
        specification_group = []
        specification_attribute = frappe.db.sql_list(
            '''select distinct sam.spec_group_name,sg.display_order from `tabSpecification Group` sg inner join `tabProduct Specification Attribute Mapping` sam on sg.name=sam.spec_group_name1 where sam.parent=%(name)s order by sam.idx''', {'name': self.name})
        if specification_attribute:
            for item in specification_attribute:
                groups = frappe.db.get_all('Product Specification Attribute Mapping', fields=[
                    'specification_attribute', 'options'], filters={"parent": self.name, 'spec_group_name': item}, order_by='idx')
                specification_group.append({"name": item, "groups": groups})
        context.specification_attribute_grouping = specification_group

        demovideo = frappe.db.get_all('Product Video', fields=[
            "*"], filters={"parent": self.name}, order_by="display_order")
        context.demo_video = demovideo
        if len(video_list) > 0:
            context.demo_video = video_list

        # recently viewed produts
        # context.recent_viewed_products = get_customer_recently_viewed_products(domain=context.get('domain'))
        if frappe.session.user != 'Guest':
            update_customer_recently_viewed(self.name)
        # recently viewed produts ended
        context.page_path = get_url()
        path = frappe.local.request.path
        context.currenturl = get_url() + path

        # get price details - check for discounts
        price_details = get_product_price(self)
        orgprice = self.price
        if price_details:
            if price_details.get('discount_amount'):
                orgprice = price_details.get('rate')
            context.discount_rule = price_details.get('discount_rule')
            context.discount_label = price_details.get('discount_label')
        if flt(orgprice) != flt(self.price):
            context.old_price = self.price
            context.price = orgprice

        if self.disable_add_to_cart_button == 1:
            self.set_product_availability(0, 'Out of Stock', context)

        elif self.inventory_method == 'Dont Track Inventory':
            self.set_product_availability(1, 'In Stock', context)
        elif self.inventory_method == 'Track Inventory':
            if self.stock == 0:
                self.set_product_availability(0, 'Out of Stock', context)
            elif self.stock > 0:
                self.set_product_availability(1, 'In Stock', context)
        else:
            self.set_product_availability(1, 'In Stock', context)
        if self.meta_title:
            context.meta_title = self.meta_title if self.meta_title else self.item
        else:
            context.meta_title = context.catalog_settings.meta_title
        if self.meta_description:
            context.meta_description = self.meta_description if self.meta_description else self.item
        else:
            context.meta_description = context.catalog_settings.meta_description

        if self.meta_keywords:
            context.meta_keywords = self.meta_keywords if self.meta_keywords else self.item
        else:
            context.meta_keywords = context.catalog_settings.meta_keywords
        allow_review = 0
        if frappe.session.user != 'Guest':
            allow_review = 1
        else:
            if context.catalog_settings.allow_anonymous_users_to_write_product_reviews:
                allow_review = 1
        context.allow_review = allow_review

        # Recent products commented and edited by Rajeshwari on 09-aug-2019

        ziprange = frappe.request.cookies.get("ziprange")
        context.ziprange = ziprange
        categories_list = frappe.db.sql('''select category, category_name from `tabProduct Category Mapping` where parent = %(parent)s order by idx limit 1''', {
            'parent': self.name}, as_dict=1)
        if categories_list:
            product_category = frappe.db.get_all('Product Category', fields=[
                "*"], filters={"name": categories_list[0].category}, order_by="display_order", limit_page_length=1)
            context.item_categories = product_category[0]
        vendor = frappe.db.sql('''select p.restaurant, b.route, b.restaurant_name from `tabProduct` p, `tabBusiness` b where b.name = p.restaurant and p.restaurant=%(restaurant)s''', {
            'restaurant': self.restaurant}, as_dict=1)
        if vendor:
            context.vendor = vendor[0]
        self.check_book_app(context)
        self.set_tax_rate(context, catalog_settings, orgprice)
        if context.map_api:
            self.check_website_product_available(context)
        product_enquiry = get_product_scroll(self.name, 1, 5)
        context.product_enquiry = product_enquiry
        if self.restaurant:
            business = frappe.get_doc("Business", self.restaurant)
            context.business_route = business.route
        context.mobile_page_title = self.item

        # created by rajeshwari on April,03-2020 for events
        if 'temple' in frappe.get_installed_apps():
            from temple.temple.api import get_related_events
            if self.product_categories:
                for x in self.product_categories:
                    if "Upcoming Events" in x.category_name:
                        context.upcoming_events_flag = 1
                        related_events = get_related_events(self.name)
                        for i in related_events:
                            if i.full_description:
                                full_description = str(
                                    remove_html_tags(i.full_description))
                                i.full_description = full_description[:95] + '...'
                        context.related_events = related_events
                    elif "Saree Sponsorship" in x.category_name:
                        context.saree_sponsorship_flag = 1
                        if self.full_description:
                            context.full_description = self.full_description
                    elif "Poojas" in x.category_name:
                        context.poojas_flag = 1
                    # elif "Deities" in x.category_name:
                    # 	context.deities_flag = 1
        control_type_check = 0
        if self.product_attributes:
            for item in self.product_attributes:
                if not "Table" in item.control_type:
                    context.control_type_check = 1

        # ends

        # updated kartheek on 17 Aug, 2020

        farming_practises = None

        check_field = frappe.db.sql(
            ''' SELECT *  FROM `tabCustom Field` where dt='Product Category' and fieldname='farming_practises' ''', as_dict=1)
        if check_field:
            if categories_list:
                product_category = frappe.db.get_all('Product Category', fields=[
                    "*"], filters={"name": categories_list[0].category}, order_by="display_order", limit_page_length=1)
                if product_category:
                    check_category = frappe.db.sql(''' SELECT farming_practises FROM `tabProduct Category` WHERE name=%(category)s''', {
                        'category': product_category[0].name}, as_dict=1)
                    if check_category:
                        if check_category[0].farming_practises:
                            farming_practises = check_category[0].farming_practises
                        else:
                            check_category = frappe.db.sql(''' SELECT farming_practises FROM `tabProduct Category` WHERE name=%(category)s''', {
                                'category': product_category[0].parent_product_category}, as_dict=1)
                            if check_category:
                                if check_category[0].farming_practises:
                                    farming_practises = check_category[0].farming_practises
        context.farming_practises = farming_practises

        # updated kartheek on 17 Aug, 2020

        # Getting Advance Amount
        advance_amount = 0
        if self.enable_preorder_product == 1:
            if self.percentage_or_amount == "Preorder Percentage":
                advance_amount += flt(self.price) * \
                    flt(self.preorder_percent) / 100
            else:
                advance_amount += flt(self.preorder_amount)
        context.advance_amount = advance_amount
        # Getting Advance Amount
        custom_values = []
        if catalog_settings.display_custom_fields == 1:
            if frappe.db.get_all("Custom Field", filters={"dt": "Product"}):
                custom_fields = frappe.db.sql(
                    '''SELECT label,fieldname FROM `tabCustom Field` WHERE dt = "Product" AND fieldtype<> "Table" AND fieldtype<> "Section Break" AND fieldtype<> "Column Break" AND fieldtype<> "HTML"  AND fieldtype<> "Check" AND fieldtype<> "Text Editor" ''', as_dict=1)
                for field in custom_fields:
                    query = "SELECT "+field.fieldname + \
                            " FROM `tabProduct` WHERE name='{0}'".format(
                                self.name)
                    custom_value = frappe.db.sql(query, as_dict=1)
                    custom_values.append(
                        {"field": field.fieldname, "label": field.label, "value": custom_value[0][field.fieldname]})
        context.custom_values = custom_values
        context.product_name = self.item.replace("'", "").replace('"', '')
        # newly updated.
        recent_products = []
        best_sellers_list = []
        if catalog_settings.detail_page_template == "Default Layout":
            recent_products = get_recent_products(business)
            best_sellers_list = get_bestsellers(business=business, limit=5)
        context.recent_products = recent_products
        context.best_sellers = best_sellers_list
    except Exception:
        frappe.log_error(frappe.get_traceback(
        ), 'ecommerce_business_store.ecommerce_business_store.product.product.get_context')


def bind_customer_cart():
    cart_items = []
    my_boxes = []
    customer_id = frappe.request.cookies.get('customer_id')

    if customer_id:
        customers = frappe.db.get_all(
            'Customers', filters={'name': customer_id}, fields=['*'])
    else:
        customers = frappe.db.get_all(
            'Customers', filters={'user_id': frappe.session.user}, fields=['*'])
    if customers:
        cart = frappe.db.get_all('Shopping Cart', filters={
            'customer': customers[0].name, 'cart_type': 'Shopping Cart'}, fields=['name', 'tax', 'tax_breakup'])
        if cart:
            cart_items = frappe.db.sql('''select c.name,c.product,c.quantity,c.attribute_description,c.attribute_ids,c.price,c.total,c.product_name,i.price,i.stock,i.short_description,i.route,
			(select cart_thumbnail from `tabProduct Image` where parent=i.name order by is_primary desc limit 1) image
			from `tabCart Items` c,`tabProduct` i where i.name=c.product and c.parent=%(parent)s order by c.idx''',
                                       {'parent': cart[0].name}, as_dict=1)
            customer = customers[0].name
            cart_settings = get_settings_from_domain('Shopping Cart Settings')
            if cart_settings and cart_settings.enable_recurring_order:
                if "subscription" in frappe.get_installed_apps():
                    active_subscription = frappe.db.sql_list('''select distinct order_reference 
						from `tabSubscription` where party_type = "Customers" and party = %(party)s 
						and status = "Active" and order_reference is not null''', {'party': customer})
                    if active_subscription:
                        reference = ','.join(
                            ['"' + x + '"' for x in active_subscription])
                        if "daily_rate" in frappe.get_installed_apps(True):
                            budget_list = frappe.db.sql('''select name, delivery_week, delivery_days, 
								tax, total, customer, order_reference from `tabMy Budget` where customer = %(customer)s 
								and order_reference in ({reference})'''.format(reference=reference),
                                {'customer': customer}, as_dict=1)
                            for item in budget_list:
                                subscription_title = frappe.db.get_all('Subscription', filters={
                                    'order_reference': item.order_reference}, fields=['name', 'subscription_title'])
                                if subscription_title:
                                    item.subscription_title = subscription_title[0].subscription_title
                                item.items = frappe.db.sql('''select c.name,c.product,c.quantity,c.price,c.total,c.product_name,c.is_free_item, c.discount_amount,
									c.attribute_description,c.attribute_ids,c.special_instruction,i.old_price, i.minimum_order_qty, i.maximum_order_qty, i.inventory_method,i.enable_shipping,i.free_shipping, i.route,ifnull((select mini_cart from `tabProduct Image` where 
									parent=i.name order by is_primary desc limit 1), '') as image,i.product_type from `tabCart Items` c,`tabProduct` 
									i where i.name=c.product and c.parent=%(parent)s order by c.creation desc''',
                                                           {'parent': item.name}, as_dict=1)
                        else:
                            budget_list = frappe.db.sql('''select name, delivery_week, delivery_days, 
								 party, order_reference from `tabSubscription` where party = %(customer)s 
								and order_reference in ({reference}) order by creation desc'''.format(reference=reference),
                                                        {'customer': customer}, as_dict=1)
                            for item in budget_list:
                                subscription_title = frappe.db.get_all('Subscription', filters={
                                    'order_reference': item.order_reference}, fields=['name', 'subscription_title'])
                                if subscription_title:
                                    item.subscription_title = subscription_title[0].subscription_title
                                item.items = frappe.db.sql('''select c.name,c.item as product,c.qty as quantity,c.price,c.total,c.item_name as product_name,c.is_free_item,
									c.attribute_description,c.attribute_ids,i.old_price, i.minimum_order_qty, i.maximum_order_qty, i.inventory_method,i.enable_shipping,i.free_shipping, i.route,ifnull((select mini_cart from `tabProduct Image` where 
									parent=i.name order by is_primary desc limit 1), '') as image,i.product_type from `tabSubscription Item` c,`tabProduct` 
									i where i.name=c.item and c.parent=%(parent)s order by c.creation desc''',
                                                           {'parent': item.name}, as_dict=1)
                        my_boxes = budget_list
    return {"cart_items": cart_items, "my_boxes": my_boxes}


@frappe.whitelist()
def get_sections():
    sections = frappe.db.sql(
        '''select name, section_type, content_type from `tabPage Section`''', as_dict=1)
    return sections


@frappe.whitelist()
def get_section_templates(device_type):
    template_groups = frappe.db.sql(
        "SELECT group_name FROM `tabSection Template Group` where name<>'Footer' AND name<>'Header' AND name <>'Page List Style' ", as_dict=1)
    templates = frappe.db.sql('''select name, image ,section_group from `tabSection Template` where ((section_group<>'Footer' AND section_group <>'Page List Style') or section_group is null) and device_type in ("Web & Mobile", %(type)s)''', {
        'type': device_type}, as_dict=1)
    return {"template_groups": template_groups, "templates": templates}


@frappe.whitelist()
def get_page_templates():
    templates = frappe.db.sql(
        '''select page_title,name,image from `tabPage Template`''', as_dict=1)
    return templates


@frappe.whitelist()
def get_footer_section_templates():
    template_groups = []
    templates = frappe.db.sql(
        '''select name, image ,section_group from `tabSection Template` where section_group='Footer' ''',  as_dict=1)
    return {"template_groups": template_groups, "templates": templates}


@frappe.whitelist()
def get_header_section_templates():
    template_groups = []
    templates = frappe.db.sql(
        '''select name, image ,section_group from `tabSection Template` where section_group='Header' ''',  as_dict=1)
    return {"template_groups": template_groups, "templates": templates}


@frappe.whitelist()
def get_list_page_templates():
    template_groups = []
    templates = frappe.db.sql(
        '''select name, image ,section_group from `tabSection Template` where section_group='Page List Style' ''',  as_dict=1)
    return {"template_groups": template_groups, "templates": templates}


@frappe.whitelist()
def get_detail_page_templates():
    template_groups = []
    templates = frappe.db.sql(
        '''select title,name, image ,layout_json from `tabDetail Page Layout`  ''',  as_dict=1)
    return {"template_groups": template_groups, "templates": templates}


@frappe.whitelist()
def get_section_columns(section, dt):
    t_fields = frappe.db.sql('''select field_label, field_key,field_type  from `tabSection Content` where parent=%(template)s ORDER BY idx ''', {
        'template': section}, as_dict=1)
    for x in t_fields:
        f_type = x.field_type
        if f_type == "Text":
            f_type = "Data"
        if f_type == "Attach":
            f_type = "Attach Image"
        x.d_fields = frappe.db.sql('''select label, fieldname  from `tabDocField` where parent=%(dt)s AND fieldtype=%(f_type)s ORDER BY idx''', {
            'dt': dt, 'f_type': f_type}, as_dict=1)
        c_fields = frappe.db.sql('''select label, fieldname  from `tabCustom Field` where dt=%(dt)s AND fieldtype=%(f_type)s ORDER BY idx''', {
            'dt': dt, 'f_type': f_type}, as_dict=1)
        for cf in c_fields:
            x.d_fields.append(cf)
    return {"t_fields": t_fields}


@frappe.whitelist()
def convert_template_to_section(template, business=None, section_name=None):
    doc = get_mapped_doc("Section Template", template, {
        "Section Template": {
            "doctype": "Page Section"
        },
        "Section Content": {
            "doctype": "Section Content"
        }
    }, None, ignore_permissions=True)

    doc.section_title = template
    # if section_name:
    # 	doc.section_title = section_name
    doc.section_name = section_name
    doc.custom_title = section_name
    doc.choose_from_template = 1
    doc.section_template = template
    if business:
        doc.business = business
    doc.save(ignore_permissions=True)
    return doc


@frappe.whitelist()
def convert_component_to_section(template):
    doc = get_mapped_doc("Section Component", template, {
        "Section Component": {
            "doctype": "Page Component"
        },
        "Section Content": {
            "doctype": "Section Content"
        }
    }, None, ignore_permissions=True)
    doc.component = template
    doc.save(ignore_permissions=True)
    return doc


@frappe.whitelist()
def update_component_page_section(page_section, comp_id, comp_uuid, cid):
    page_section = frappe.get_doc("Page Section", page_section)
    if page_section:
        component_fields = frappe.db.get_all("Section Content", filters={
            "parent": comp_uuid}, fields=['*'])
        comp_info = frappe.get_doc("Section Component", comp_uuid)
        for x in component_fields:
            page_section.append("content", {
                "component_ref": comp_id,
                "field_type": x.field_type,
                "content_type": x.content_type,
                "image_dimension": x.image_dimension,
                "allow_update_to_style": x.allow_update_to_style,
                "css_properties_list": x.css_properties_list,
                "content": x.content,
                "fields_json": x.fields_json,
                "css_json": x.css_json,
                "css_text": x.css_text,
                "field_label": x.field_label,
                "field_key": x.field_key,
                "group_name": x.group_name,
                "component_id": comp_uuid,
                "component_type": comp_info.component_type,
                "cid": cid,
            })
        page_section.save(ignore_permissions=True)
        return {"comp_info": comp_info, "layout_json": json.loads(page_section.layout_json)}


@frappe.whitelist()
def delete_section(name, parentfield, fc_name=None, doctype=None):
    page_section = frappe.db.get_all("Mobile Page Section", filters={
        "name": name}, fields=['section'])
    frappe.db.sql('''delete from `tabMobile Page Section` where name = %(name)s and parentfield = %(parentfield)s''', {
        'name': name, 'parentfield': parentfield})
    if page_section:
        frappe.delete_doc('Page Section', page_section[0].section)
        # frappe.db.sql('''delete from `tabPage Section` where name = %(name)s''', {
        #     'name': page_section[0].section})
        # frappe.db.commit()
    if fc_name and doctype:
        if frappe.db.exists(doctype, fc_name, cache=True):
            doc = frappe.get_doc(doctype, fc_name)
            doc.save()

    return {'status': 'Success'}


@frappe.whitelist()
def get_section_content(section, content_type):
    section = frappe.db.get_all('Page Section', filters={'name': section}, fields=[
        'section_type', 'name', 'form', 'html_content', 'reference_document', 'fetch_product', 'reference_name', 'no_of_records', 'custom_section_data', 'display_data_randomly', 'dynamic_data', 'is_login_required', 'allow_update_to_style', 'menu', 'section_title', 'class_name', 'css_json', 'is_full_width'
    ])

    if section:
        section[0].content = frappe.db.sql('''select field_label, field_key, field_type, content,allow_update_to_style, css_properties_list, name, group_name, fields_json,css_json,css_text,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and parenttype = "Page Section" order by idx''', {
            'parent': section[0].name, 'content_type': content_type}, as_dict=1)
        # if section[0].content[0]['css_properties_list']:section[0].content[0]['css_properties_list']=json.loads(section[0].content[0]['css_properties_list'])
        # if section[0].section_title:
        # 	style_fields = frappe.get_list("Section Template",filters={"name":section[0].section_title},fields={"css_field_list","allow_update_to_style"})
        # 	if style_fields:styles = style_fields[0]['css_field_list']
        # frappe.log_error(styles,"styles")
    # styles = frappe.db.get_single_value("CMS Settings","styles_to_update")
    # frappe.log_error(styles)
    # if styles:
    # 	section[0].styles =  json.loads((styles))
    # section[0]['allow_update_to_style']= style_fields[0]['allow_update_to_style']
    # if section[0]['css_json']:section[0]['css_json']=json.loads(section[0]['css_json'])
    # frappe.log_error(section[0],"section[0]")
    fonts_list = frappe.db.get_all("CSS Font", fields=['name', 'font_family'])
    section[0].fonts_list = fonts_list
    return section[0]


@frappe.whitelist()
def get_component_content(section, content_type):
    section = frappe.db.get_all('Page Component', filters={'name': section}, fields=[
        'name', 'allow_update_to_style', 'css_field_list', 'title', 'css_field_list'])
    if section:
        section[0].content = frappe.db.sql('''select field_label, field_key, field_type, content,allow_update_to_style, css_properties_list, name, group_name, fields_json,css_json,css_text,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and parenttype = "Page Component" order by idx''', {
            'parent': section[0].name, 'content_type': content_type}, as_dict=1)
        fonts_list = frappe.db.get_all(
            "CSS Font", fields=['name', 'font_family'])
        section[0].fonts_list = fonts_list
        return section[0]


@frappe.whitelist()
def get_page_component_content(section, comp_id, content_type, cid):
    section = frappe.db.get_all('Page Section', filters={'name': section}, fields=[
        'name', 'allow_update_to_style', 'css_field_list', 'title', 'css_field_list'])
    if section:
        if comp_id:
            section[0].content = frappe.db.sql('''select field_label, field_key, field_type, content,allow_update_to_style, css_properties_list, name, group_name, fields_json,css_json,css_text,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and component_ref = %(comp_id)s and cid=%(cid)s order by idx''', {
                'cid': cid, 'comp_id': comp_id, 'parent': section[0].name, 'content_type': content_type}, as_dict=1)
            fonts_list = frappe.db.get_all(
                "CSS Font", fields=['name', 'font_family'])
            section[0].fonts_list = fonts_list
            return section[0]
        else:
            section[0].content = frappe.db.sql('''select field_label, field_key, field_type, content,allow_update_to_style, css_properties_list, name, group_name, fields_json,css_json,css_text,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s  order by idx''', {
                'cid': cid, 'comp_id': comp_id, 'parent': section[0].name, 'content_type': content_type}, as_dict=1)
            fonts_list = frappe.db.get_all(
                "CSS Font", fields=['name', 'font_family'])
            section[0].fonts_list = fonts_list
            return section[0]


@frappe.whitelist()
def get_component_properties(page_section, comp_ref, cid):
    comps = frappe.db.sql(""" SELECT component_id FROM `tabSection Content` WHERE parent=%(page_section)s AND component_ref = %(comp_ref)s AND cid=%(cid)s """, {
        "page_section": page_section, "comp_ref": comp_ref, "cid": cid}, as_dict=1)
    if comps:
        comp_info = frappe.get_doc("Section Component", comps[0].component_id)
        if comp_info.allow_update_to_style:
            if comp_info.css_field_list:
                return {"status": "success", "css_field_list": css_field_list}
    return {"status": "Failed", "message": "No styles to update"}


@frappe.whitelist()
def get_section_properties(section_name):
    content_type = 'Data'
    allow_update_to_style = 0
    p_sections = frappe.db.get_all("Mobile Page Section", filters={
        "name": section_name}, fields=['section'])
    if p_sections:
        section = p_sections[0].section
        styles = style_fields = None
        section = frappe.db.get_all('Page Section', filters={'name': section}, fields=['section_type', 'name', 'reference_document', 'fetch_product', 'reference_name', 'no_of_records',
                                                                                       'custom_section_data', 'dynamic_data', 'is_login_required', 'allow_update_to_style', 'menu', 'section_title', 'class_name', 'css_json', 'is_full_width', 'css_field_list'])
        if section:
            section[0].content = frappe.db.sql('''select field_label, field_key, field_type, content,allow_update_to_style, css_properties_list, name, group_name, fields_json,css_json,css_text,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and parenttype = "Page Section" order by idx''', {
                'parent': section[0].name, 'content_type': content_type}, as_dict=1)
            if section[0].content:
                if section[0].content[0]['css_properties_list']:
                    section[0].content[0]['css_properties_list'] = json.loads(
                        section[0].content[0]['css_properties_list'])
            if section[0].section_title:
                style_fields = frappe.get_list("Section Template", filters={
                    "name": section[0].section_title}, fields={"css_field_list", "allow_update_to_style"})
                if style_fields:
                    styles = style_fields[0]['css_field_list']
                    allow_update_to_style = style_fields[0]['allow_update_to_style']
                if not style_fields:
                    # style_fields = frappe.get_list("Page Section",filters={"name":section},fields={"css_field_list","allow_update_to_style"})
                    styles = section[0].css_field_list
                    allow_update_to_style = 1
                # frappe.log_error(styles,"styles")
        # styles = frappe.db.get_single_value("CMS Settings","styles_to_update")
        # frappe.log_error(styles)
        if styles:
            section[0].styles = json.loads((styles))
        section[0]['allow_update_to_style'] = allow_update_to_style
        if section[0]['css_json']:
            section[0]['css_json'] = json.loads(section[0]['css_json'])
        # frappe.log_error(section[0],"section[0]")
        fonts_list = frappe.db.get_all(
            "CSS Font", fields=['name', 'font_family'])
        section[0].fonts_list = fonts_list
        return section[0]


@frappe.whitelist()
def get_page_section_properties(section_name):
    content_type = 'Data'
    section = section_name
    styles = style_fields = None
    section = frappe.db.get_all('Page Section', filters={'name': section}, fields=['section_type', 'name', 'reference_document', 'fetch_product', 'reference_name', 'no_of_records',
                                                                                   'custom_section_data', 'dynamic_data', 'is_login_required', 'allow_update_to_style', 'menu', 'section_title', 'class_name', 'css_json', 'is_full_width'])
    if section:
        section[0].content = frappe.db.sql('''select field_label, field_key, field_type, content,allow_update_to_style, css_properties_list, name, group_name, fields_json,css_json,css_text,image_dimension from `tabSection Content` where parent = %(parent)s and content_type = %(content_type)s and parenttype = "Page Section" order by idx''', {
            'parent': section[0].name, 'content_type': content_type}, as_dict=1)
        if section[0].content:
            if section[0].content[0]['css_properties_list']:
                section[0].content[0]['css_properties_list'] = json.loads(
                    section[0].content[0]['css_properties_list'])
        if section[0].section_title:
            style_fields = frappe.get_list("Field Types Property", filters={
                "field_type": "Page Section"}, fields={"css_properties_list"})
            if style_fields:
                styles = style_fields[0]['css_properties_list']
    if styles:
        section[0].styles = json.loads((styles))
    section[0]['allow_update_to_style'] = 1
    if section[0]['css_json']:
        section[0]['css_json'] = json.loads(section[0]['css_json'])
    fonts_list = frappe.db.get_all("CSS Font", fields=['name', 'font_family'])
    section[0].fonts_list = fonts_list
    return section[0]


@frappe.whitelist()
def get_column_properties(section_name, column):
    styles = update_css = None
    css_properties = frappe.db.get_all("Field Types Property", fields=['css_properties_list'], filters={
        "parent": "CMS Settings", "field_type": "Section Column"})
    if css_properties:
        styles = json.loads(css_properties[0].css_properties_list)
    fonts_list = frappe.db.get_all("CSS Font", fields=['name', 'font_family'])
    css_json = frappe.db.get_all("Section Column CSS", filters={
        "parent": section_name, "column_class": column}, fields=['css_json'])
    if css_json:
        update_css = json.loads(css_json[0].css_json)
    return {"fonts_list": fonts_list, "styles": styles, 'css_json': update_css, "class_name": column}


@frappe.whitelist()
def update_section_properties(section_name, css_design, style_json, is_full_width):
    content_type = 'Data'
    p_sections = frappe.db.get_all("Mobile Page Section", filters={
        "name": section_name}, fields=['section'])
    if p_sections:
        section = p_sections[0].section
        page_section = frappe.get_doc("Page Section", section)
        page_section.css_text = css_design
        page_section.css_json = (style_json)
        page_section.is_full_width = is_full_width
        page_section.save()
        return "success"


@frappe.whitelist()
def remove_page_section(page_route, page_section):
    pages = frappe.db.get_all(
        "Web Page Builder", filters={"route": page_route})
    if pages:
        m_section = frappe.db.get_all("Mobile Page Section", filters={
            "parent": pages[0].name, "section": page_section})
        if m_section:
            frappe.db.sql("DELETE FROM `tabMobile Page Section` WHERE name=%(m_id)s", {
                "m_id": m_section[0].name})
            frappe.db.commit()
            frappe.db.sql("DELETE FROM `tabPage Section` WHERE name=%(m_id)s", {
                "m_id": page_section})
            frappe.db.commit()
            page_builder = frappe.get_doc("Web Page Builder", pages[0].name)
            page_builder.save()


@frappe.whitelist()
def remove_page_section_component(page_section, uid, cid):
    page_sec = frappe.db.get_all("Page Section", filters={
        "name": page_section}, fields=['name', 'layout_json'])
    if page_sec:
        frappe.db.sql("DELETE FROM `tabSection Content` WHERE parent=%(p_id)s AND component_ref=%(uid)s and cid=%(cid)s", {
            "p_id": page_section, "uid": uid, "cid": cid})
        frappe.db.commit()
        for x in page_sec:
            x.layout_json = json.loads(x.layout_json)
        return page_sec[0]


@frappe.whitelist()
def get_page_layout_json(page_route):
    pages = frappe.db.get_all(
        "Web Page Builder", filters={"route": page_route})
    if pages:
        page_sections = frappe.db.sql(""" SELECT P.name as page_section ,P.layout_json,P.layout_id,P.layout_type,MP.section_title FROM `tabMobile Page Section` MP 
										INNER JOIN `tabPage Section` P ON MP.section= P.name
										WHERE MP.parent = %(page_id)s ORDER BY MP.idx""", {"page_id": pages[0].name}, as_dict=1)
        for x in page_sections:
            if x.layout_json:
                x.layout_json = json.loads(x.layout_json)
        cid = 0
        cid_list = frappe.db.sql(""" SELECT CAST(cid AS UNSIGNED) as cid FROM `tabSection Content` SC
									   INNER JOIN `tabPage Section` PS ON SC.parent = PS.name
									   INNER JOIN `tabMobile Page Section` MP ON MP.section = PS.name
									   INNER JOIN `tabWeb Page Builder` PB ON PB.name = MP.parent  
									   WHERE  PB.route=%(pb_route)s order by cid  desc limit 1""", {'pb_route': page_route}, as_dict=1)
        if cid_list:
            cid = cid_list[0].cid
        pb_list = frappe.db.get_all(
            "Web Page Builder", filters={"route": page_route})
        return {"page_sections": page_sections, 'cid': cid, 'title': pb_list[0].name}
    return []


@frappe.whitelist()
def get_builder_data(page_route):
    pages = frappe.db.get_all(
        "Web Page Builder", filters={"route": page_route})
    if pages:
        page_sections = frappe.db.sql(""" SELECT P.name as page_section ,P.layout_json,P.layout_id,P.layout_type,MP.section_title FROM `tabMobile Page Section` MP 
										INNER JOIN `tabPage Section` P ON MP.section= P.name
										WHERE MP.parent = %(page_id)s ORDER BY MP.idx""", {"page_id": pages[0].name}, as_dict=1)
        for x in page_sections:
            if x.layout_json:
                x.layout_json = json.loads(x.layout_json)
        cid = 0
        cid_list = frappe.db.sql(""" SELECT CAST(cid AS UNSIGNED) as cid FROM `tabSection Content` SC
									   INNER JOIN `tabPage Section` PS ON SC.parent = PS.name
									   INNER JOIN `tabMobile Page Section` MP ON MP.section = PS.name
									   INNER JOIN `tabWeb Page Builder` PB ON PB.name = MP.parent  
									   WHERE  PB.route=%(pb_route)s order by cid  desc limit 1""", {'pb_route': page_route}, as_dict=1)
        if cid_list:
            cid = cid_list[0].cid
        pb_list = frappe.db.get_all(
            "Web Page Builder", filters={"route": page_route})
        pages_list = frappe.db.sql(
            """ SELECT name , route FROM `tabWeb Page Builder` WHERE published=1 AND (w_page_type IS NULL OR w_page_type ='Regular') """, as_dict=1)
        return {"page_sections": page_sections, 'cid': cid, 'title': pb_list[0].name, "pages_list": pages_list}
    return []


@frappe.whitelist()
def update_layout_json(page_route, layout_json):
    page_builder = frappe.db.get_all(
        "Web Page Builder", filters={"route": page_route})
    if page_builder:
        p_builder = frappe.get_doc("Web Page Builder", page_builder[0].name)
        p_builder.layout_json = layout_json
        p_builder.save(ignore_permissions=True)


@frappe.whitelist()
def update_page_section_layout_json(page_section, layout_json):
    page_section = frappe.db.get_all(
        "Page Section", filters={"name": page_section})
    if page_section:
        p_builder = frappe.get_doc("Page Section", page_section[0].name)
        p_builder.layout_json = layout_json
        p_builder.save(ignore_permissions=True)


@frappe.whitelist()
def update_page_section_properties(section_name, css_design, style_json, is_full_width):
    content_type = 'Data'
    page_section = frappe.get_doc("Page Section", section_name)
    page_section.css_text = css_design
    page_section.css_json = (style_json)
    page_section.is_full_width = is_full_width
    page_section.save()
    return "success"


@frappe.whitelist()
def update_page_section_column_properties(section_name, css_design, style_json, column):
    content_type = 'Data'
    check_already = frappe.db.get_all("Section Column CSS", filters={
        "parent": section_name, "column_class": column})
    if check_already:
        scc = frappe.get_doc("Section Column CSS", check_already[0].name)
        scc.css_text = css_design
        scc.css_json = (style_json)
        scc.save()
    else:
        page_section = frappe.get_doc("Page Section", section_name)
        page_section.append("section_column_css", {
            "css_text": css_design,
            "css_json": style_json,
            "column_class": column
        })
        page_section.save()

    return "success"
# updated by boopathy


@frappe.whitelist()
def generate_css_file():
    path = get_files_path()
    if not os.path.exists(os.path.join(path, 'site_custom_css.css')):
        res = frappe.get_doc({
            "doctype": "File",
            "file_name": "site_custom_css.css",
            "is_private": 1,
        })
    css_content = ''
    css_fonts = frappe.db.get_all(
        "CSS Font", fields=['font_name', 'font_type', 'font_url', 'font_family'])
    for x in css_fonts:
        if x.font_type == "Google":
            css_content += "@import url('"+x.font_url+"');"
    pages = frappe.db.get_all("Web Page Builder", filters={
        "published": 1, "use_page_builder": 1})
    for page in pages:
        web_sections = frappe.db.sql("""SELECT P.css_text,P.name FROM `tabMobile Page Section` M INNER JOIN `tabPage Section` P ON M.section=P.name WHERE M.parent = %(page_name)s""", {
            "page_name": page.name}, as_dict=1)
        for x in web_sections:
            if x.css_text:
                css_content += x.css_text
            section_content = frappe.db.get_all("Section Content", filters={
                "parent": x.name}, fields=['css_text'])
            for field in section_content:
                if field.css_text:
                    css_content += field.css_text
    if css_content:
        with open(os.path.join(path, ('site_custom_css.css')), "w") as f:
            f.write(css_content)
    # import os
    # from frappe.utils import get_files_path
    # path = get_files_path()
    # with open(os.path.join(path,'test.css'), "w") as f:
    # 	content = content
    # 	f.write(content)
    # return {"status":"success","message":"completed successfully"}


# end


@frappe.whitelist()
def update_section_content(docs, section, lists_data='[]', business=None, template=None):
    # hided by boopathy
    # from ecommerce_business_store.ecommerce_business_store.mobileapi import get_uploaded_file_content, update_doc
    # end
    if lists_data:
        lists = json.loads(lists_data)
        for li in lists:
            dt, image_option, image_docs = frappe.db.get_value('Page Section', section, [
                'reference_document', 'image_option', 'image_link_documents'])
            if li.get('image_type') == 'Random images from associated products':
                li['image'] = get_random_images(dt, li.get('item'), business, li.get(
                    'image_ref_doc'), image_option, image_docs)
            if li.get('image_type') == 'Image attached to document':
                li['image'] = get_document_image(dt, li.get('item'), business)
            try:
                if not li.get('route'):
                    dt = frappe.db.get_value(
                        'Page Section', section, 'reference_document')
                    li['route'] = dt = frappe.db.get_value(
                        dt, li.get('item'), 'route')
            except Exception as e:
                pass
        lists_data = json.dumps(lists)
    frappe.db.set_value('Page Section', section,
                        'custom_section_data', lists_data)
    # frappe.db.commit()
    return_data = []
    for item in json.loads(docs):
        if item.get('content') and str(item.get('content')).find(',data:image/') != -1 and str(item.get('content')).find(';base64,') != -1:
            filedata = 'data:{0}'.format(
                item.get('content').split(',data:')[1])
            content = get_uploaded_file_content(filedata)
            res = frappe.utils.file_manager.save_file(item.get('content').split(
                ',data:image/')[0], content, item.get('doctype'), item.get('parent'))
            if res:
                item['content'] = res.file_url
        if item.get('name') not in ['category_products_html', 'blog_category_html', 'display_data_randomly', 'dynamic_data', 'reference_name', 'fetch_product', 'no_of_records', 'collections', 'menu', 'form', 'html_content', 'section_css_json', 'section_css_text', 'is_full_width']:
            update_doc(item)
            if str(item.get("content")).startswith("/files") and ".svg" not in str(item.get("content")):
                sec_content = frappe.get_doc(
                    "Section Content", item.get("name"))
                if sec_content.image_dimension:
                    width = int(
                        sec_content.image_dimension.lower().split('x')[0])
                    height = int(
                        sec_content.image_dimension.lower().split('x')[1])
                    if frappe.db.get_all("File", filters={"file_url": item.get("content")}):
                        org_file_doc = frappe.get_doc("File", {
                            "file_url": item.get("content"),
                        })
                        if org_file_doc:
                            from PIL import Image
                            from io import BytesIO
                            import base64
                            import os
                            from frappe.utils import get_files_path
                            path = get_files_path()
                            file_url = item.get("content")
                            file_url = file_url.rpartition('/')[2]
                            file_path = path+"/"+file_url
                            buffered = BytesIO()
                            img = Image.open(file_path)
                            extn = "PNG"
                            if "jpg" in file_url.lower() or "jpeg" in file_url.lower():
                                extn = "JPEG"
                            img.save(buffered, format=extn,
                                     optimize=True, quality=40)
                            img_str = base64.b64encode(buffered.getvalue())
                            ret = frappe.get_doc({"doctype": "File",
                                                  "file_name": item.get("name")+"_"+file_url,
                                                  "is_private": 0,
                                                  "content": img_str,
                                                  "decode": True,
                                                  "folder": "Home",
                                                  "attached_to_name": item.get("name"),
                                                  "attached_to_doctype": "Section Content",
                                                  })
                            ret.insert()
                            return_url = ret.make_thumbnail(
                                set_as_thumbnail=False, width=width, height=height, suffix=str(height))
                            # frappe.log_error(return_url,"dm")
                            item["content"] = return_url
                            update_doc(item)
        else:
            if item.get('name') == 'reference_name':
                frappe.db.set_value('Page Section', section,
                                    'reference_name', item.get('content'))
            elif item.get('name') == 'fetch_product':
                frappe.db.set_value('Page Section', section,
                                    'fetch_product', item.get('content'))
            elif item.get('name') == 'no_of_records':
                frappe.db.set_value('Page Section', section,
                                    'no_of_records', item.get('content'))
            elif item.get('name') == 'collections':
                frappe.db.set_value('Page Section', section,
                                    'collections', item.get('content'))
            elif item.get('name') == 'menu':
                frappe.db.set_value('Page Section', section,
                                    'menu', item.get('content'))
            elif item.get('name') == 'form':
                frappe.db.set_value('Page Section', section,
                                    'form', item.get('content'))
            elif item.get('name') == 'html_content':
                doc_update = frappe.get_doc('Page Section', section)
                doc_update.html_content = item.get('content')
                doc_update.save()
            elif item.get('name') == 'section_css_text':
                # frappe.log_error("css_text",item.get('content'))
                frappe.db.set_value('Page Section', section,
                                    'css_text', item.get('content'))
            elif item.get('name') == 'section_css_json':
                # frappe.log_error("css_json",item.get('content'))
                frappe.db.set_value('Page Section', section,
                                    'css_json', json.dumps(item.get('content')))
            elif item.get('name') == 'is_full_width':
                # frappe.log_error("css_json",item.get('content'))
                frappe.db.set_value('Page Section', section,
                                    'is_full_width', item.get('content'))
            elif item.get('name') == 'dynamic_data':
                # frappe.log_error("css_json",item.get('content'))
                frappe.db.set_value('Page Section', section,
                                    'dynamic_data', item.get('content'))
            elif item.get('name') == 'display_data_randomly':
                # frappe.log_error("css_json",item.get('content'))
                check_val = 0
                if item.get('content'):
                    check_val = item.get('content')
                frappe.db.set_value('Page Section', section,
                                    'display_data_randomly', check_val)
            elif item.get('name') == "category_products_html":
                # hided by boopathy on 10/08/2022
                # from ecommerce_business_store.ecommerce_business_store.api import get_product_details
                # end
                if item.get('content') and item.get('content') != "":
                    products = json.loads(item.get('content'))
                    p_ids = []
                    order_by = ''
                    for x in products:
                        p_ids.append(x.get("name"))
                        order_by += x.get("name")+","
                    products_filters = ','.join(['"' + x + '"' for x in p_ids])
                    if products_filters:
                        conditions = "  p.name in("+products_filters+")"
                        books_join_query = ''
                        books_columns_query = ''

                        installed_apps = frappe.db.sql(
                            ''' select * from `tabModule Def` where app_name='book_shop' ''', as_dict=True)
                        if len(installed_apps) > 0:
                            books_columns_query = ',AU.author_name,AU.route as author_route,PU.publisher_name,PU.route as publisher_route'
                            books_join_query = '  left join `tabAuthor` AU on AU.name=p.author left join `tabPublisher` PU on PU.name=p.publisher'
                        query = "select distinct p.item,p.restaurant,p.price,p.old_price,p.short_description,p.tax_category,p.full_description,p.sku,p.name,p.route,p.inventory_method,p.is_gift_card,(case when inventory_method ='Track Inventory' then p.stock else  10000 end) as stock,p.minimum_order_qty,p.maximum_order_qty,p.disable_add_to_cart_button,p.enable_preorder_product,p.weight,p.gross_weight,p.approved_total_reviews,CM.category,\
						pc.show_attributes_inlist,pc.products_per_row_for_mobile_app,\
													(select list_image from `tabProduct Image` where parent=p.name order by is_primary desc limit 1) as product_image,\
													(select brand_name from `tabProduct Brand Mapping` where parent=p.name limit 1) as product_brand,\
													(select B.route from `tabProduct Brand Mapping` MP\
													inner join `tabProduct Brand` B on MP.brand=B.name\
													where MP.parent=p.name and B.published=1 limit 1) as brand_route" \
                                + books_columns_query + ' from `tabProduct` p ' + books_join_query \
                                + " inner join `tabProduct Category Mapping` CM on CM.parent=p.name\
							inner join `tabProduct Category` pc on CM.category=pc.name\
													where p.is_active=1 and p.status='Approved' and  %s group by p.name ORDER BY FIND_IN_SET(p.name,'%s')" \
                                % (conditions, order_by[:-1])
                        # frappe.log_error(query,"query")
                        products = frappe.db.sql(query, as_dict=1)
                        # products = frappe.db.sql(""" SELECT route,name,item,short_description,full_description,price,old_price FROM `tabProduct` WHERE name in (%s) """%(products_filters),as_dict=1)
                        # for x in products:
                        # x.images = frappe.db.sql('''select detail_thumbnail, title, is_primary, image_name, product_image, detail_image,name from `tabProduct Image` where parent = %(parent)s order by is_primary desc, idx''',{'parent': x.name},as_dict=1)
                        result = get_product_details(products)
                        # frappe.log_error(result,'result')
                        frappe.db.set_value('Page Section', section, 'custom_section_data', json.dumps(
                            result, indent=1, sort_keys=False, default=str))
                    else:
                        frappe.db.set_value(
                            'Page Section', section, 'custom_section_data', "[]")

                else:
                    frappe.db.set_value(
                        'Page Section', section, 'custom_section_data', "[]")
            elif item.get('name') == "blog_category_html":
                if item.get('content') and item.get('content') != "":
                    products = json.loads(item.get('content'))
                    p_ids = []
                    order_by = ''
                    for x in products:
                        p_ids.append(x.get("name"))
                        order_by += x.get("name")+","
                    products_filters = ','.join(['"' + x + '"' for x in p_ids])
                    if products_filters:
                        conditions = "  p.name in("+products_filters+")"
                        query = "select distinct * from `tabBlog Post` p where p.published=1 and  %s group by p.name ORDER BY FIND_IN_SET(p.name,'%s')" \
                                % (conditions, order_by[:-1])
                        # frappe.log_error(query,"query")
                        result = frappe.db.sql(query, as_dict=1)
                        # result = get_product_details(products)

                        frappe.db.set_value('Page Section', section, 'custom_section_data', json.dumps(
                            result, indent=1, sort_keys=False, default=str))
                    else:
                        frappe.db.set_value(
                            'Page Section', section, 'custom_section_data', "[]")

                else:
                    frappe.db.set_value(
                        'Page Section', section, 'custom_section_data', "[]")
        item["field_key"] = frappe.db.get_value(
            "Section Content", item.get("name"), "field_key")
        item["component_type"] = frappe.db.get_value(
            "Section Content", item.get("name"), "component_type")
        if item["component_type"]:
            item['component_title'] = frappe.db.get_value("Section Component", frappe.db.get_value(
                "Section Content", item.get("name"), "component_id"), "title")
        return_data.append(item)
    ps_json = frappe.db.get_value("Page Section", section, 'layout_json')
    ps_layout_json = []
    if ps_json:
        ps_layout_json = json.loads(ps_json)

    return {'status': 'Success', 'data': return_data, 'layout_json': ps_layout_json}


@frappe.whitelist()
def get_random_records(dt, records, business=None):
    fields = condition = ''
    if not business:
        business = get_business_from_login()
    if dt == 'Product Category':
        fields = 'name as item, category_name as item_title, category_name as item_name, route'
        condition = 'where is_active = 1'
        if business:
            condition += ' and business = "{0}"'.format(business)
    elif dt == 'Product Brand':
        fields = 'name as item, brand_name as item_title, brand_name as item_name, route'
        condition = 'where published = 1'
        if business:
            condition += ' and business = "{0}"'.format(business)
    elif dt == 'Product':
        fields = 'name as item, item as item_title, item as item_name, route'
        condition = 'where is_active = 1 and status = "Approved"'
        if business:
            condition += ' and restaurant = "{0}"'.format(business)
    if fields and fields != '':
        return frappe.db.sql('''select d.*, "Random images from associated products" as image_type, 
			(@row_number:=@row_number + 1) AS idx from (select {fields} from `tab{dt}`, (SELECT @row_number:=0) AS t {cond} order by rand() limit {limit}) d order by idx'''.format(fields=fields, dt=dt, cond=condition, limit=records), as_dict=1)


@frappe.whitelist()
def get_predefined_records(dt, records, name, page_no=0, business=None):
    if name:
        quer_info = frappe.db.get_value(
            'Page Section', name, 'predefined_section')
        query = frappe.db.get_value('Custom Query', quer_info, 'query')
    if int(records) > 0:
        start = int(page_no) * int(records)
        query = '{0} limit {1},{2}'.format(query, start, records)
    if not business:
        business = get_business_from_login()
    try:
        result = frappe.db.sql('''{query}'''.format(query=query), as_dict=1)
        # if result and dt == 'Product':
        # 	result = get_product_details(result)
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(
        ), "ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.get_predefined_records")
        return []


@frappe.whitelist()
def get_image_album(dt, dn, business=None):
    if not business:
        business = get_business_from_login()
    condition = ''
    if business:
        condition = ' and p.restaurant = "{0}"'.format(business)
    if dt == "Product Category":
        products = frappe.db.sql_list(
            '''select m.parent from `tabProduct Category Mapping` m inner join tabProduct p on p.name = m.parent where m.category = %(name)s {cond} group by p.name'''.format(cond=condition), {'name': dn})
    elif dt == "Product Brand":
        products = frappe.db.sql_list(
            '''select m.parent from `tabProduct Brand Mapping` m inner join tabProduct p on p.name = m.parent where m.brand = %(name)s {cond} group by p.name'''.format(cond=condition), {'name': dn})
    elif dt == "Product":
        products = [dn]

    if products and len(products) > 0:
        product_list = ",".join(['"' + i + '"' for i in products])
        return frappe.db.sql('''select list_image, detail_thumbnail as thumbnail from `tabProduct Image` where parent in ({product}) order by idx'''.format(product=product_list), as_dict=1)

    return []


@frappe.whitelist()
def get_patterns_list():
    return frappe.db.sql('''select name, background_color, background_image, heading_text_color, view_all_bg_color, view_all_text_color from `tabPage Pattern`''', as_dict=1)


@frappe.whitelist()
def update_patterns(**kwargs):
    keys = kwargs.keys()
    keys = list(keys)
    if keys and 'cmd' in keys:
        keys.remove('cmd')
    if keys and 'name' in keys:
        keys.remove('name')
    if keys and 'section' in keys:
        keys.remove('section')
    field_names = ",".join(['"' + i + '"' for i in keys])
    if kwargs.get('section'):
        section_content = frappe.db.sql('''select name, field_key from `tabSection Content` where parent = %(parent)s and field_key in ({keys})'''.format(
            keys=field_names), {'parent': kwargs.get('section')}, as_dict=1)
        if section_content:
            for item in keys:
                check = next(
                    (x for x in section_content if x.field_key == item), None)
                if check:
                    frappe.db.set_value(
                        'Section Content', check.name, 'content', kwargs.get(item))
                else:
                    frappe.get_doc({
                        "doctype": "Section Content", "parent": kwargs.get('section'), "parenttype": "Page Section",
                        "field_key": item, "content": kwargs.get('content'), "content_type": "Design", "parentfield": "content"
                    }).insert(ignore_permissions=True)
    return {'status': 'Success'}


def get_page_section(source_doc):
    data = []
    path = get_files_path()
    file_path = os.path.join(path, source_doc)
    if os.path.exists(file_path):
        # frappe.log_error(file_path,">> file path <<")
        with open(file_path) as f:
            data = json.loads(f.read())
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


def get_page_html(doc, sections, html, source_doc, device_type, blog_name=None, add_info=None, page_no=0, page_len=3):
    section_list = sections[int(page_no):int(page_len)]
    data = get_page_section(source_doc)
    html_list = []
    js_list = ''
    res = {}
    for item in section_list:
        section_html, css, js, reference_document, form_doc, html_content = frappe.db.get_value(
            'Page Section', item.section, [html, 'custom_css', 'custom_js', 'reference_document', 'form', 'html_content'])
        if section_html:
            if css:
                if css.find('<style') == -1:
                    section_html += '<style>{0}</style>'.format(css)
                else:
                    section_html += '{0}'.format(css)
            if js:
                js = js.replace('&amp;', '&').replace('&gt;', '>')
                if js.find('<script') == -1:
                    if page_no == 0:
                        js_list += frappe.render_template(
                            '<script>{0}</script>'.format(js), item.as_dict())
                        section_html += frappe.render_template(
                            '<script>{0}</script>'.format(js), item.as_dict())

                    else:
                        section_html += '<script>{0}</script>'.format(js)
                else:
                    if page_no == 0:
                        js_list += frappe.render_template(
                            '{0}'.format(js), item.as_dict())
                        section_html += frappe.render_template(
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
                pg_doc = frappe.get_doc('Page Section', item.section)
                data_source['data'] = get_data_source(
                    pg_doc.query, pg_doc.reference_document, pg_doc.no_of_records, 1, business=pg_doc.business)
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
            data_source['name_section'] = item.section
            data_source['route_prefix'] = doc.route_prefix if doc.route_prefix else ""
            data_source['html_content'] = html_content or ''

            if form_doc and frappe.db.exists('MBW Form', form_doc):
                form_data = frappe.get_doc('MBW Form', form_doc).as_dict()
                for field in form_data.form_fields:
                    if field.field_type in ['checkbox', 'radio', 'select']:
                        field['field_options'] = str(
                            field.field_options).split('\n')
                data_source['form_data'] = form_data

            if blog_name and frappe.db.exists("Mbw Blog Post", blog_name):
                blog_detail = frappe.get_doc(
                    'Mbw Blog Post', blog_name)
                blog_detail.published_on = blog_detail.published_on.strftime(
                    "%d-%m-%Y")
                data_source['blog_detail'] = blog_detail

                breadcrumb = data_source.get('breadcrumb')
                if breadcrumb:
                    breadcrumb.append({
                        'idx': len(breadcrumb) + 1,
                        'menu': blog_detail.title,
                        'route': "#"
                    })
                    data_source['breadcrumb'] = breadcrumb
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
                # frappe.log_error(section_html,">> section_html <<")
                import datetime as dt
                data_doc = data_source.get('data')
                if data_doc:
                    for i in data_doc:
                        published_on = i.get('published_on')
                        if published_on and isinstance(published_on, dt.date):
                            i['published_on'] = published_on.strftime(
                                "%d-%m-%Y")
                    data_source['data'] = data_doc
                template = frappe.render_template(section_html, data_source)
                html_list.append(
                    {'template': template, 'section': item.section})
            except Exception as e:
                frappe.log_error(frappe.get_traceback(
                ), "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_page_html")
    return html_list, js_list


@frappe.whitelist(allow_guest=True)
def get_more_post(name_section, page_no=1, page_len=8):
    doc_section = frappe.get_doc('Page Section', name_section)
    sort_field = doc_section.sort_field if doc_section.sort_field else 'published_on'
    limit = doc_section.no_of_records if doc_section.no_of_records else page_len
    offset = page_no*limit
    query = '''SELECT * FROM `tab{doctype}` doc WHERE {condition} order by {sort_field} {sort_by} LIMIT {limit} OFFSET {offset}'''.format(
        doctype=doc_section.reference_document, condition=doc_section.condition, sort_field=doc_section.sort_field, sort_by=doc_section.sort_by, limit=limit, offset=offset)

    data = frappe.db.sql(query, as_dict=1)
    for item in data:
        published_on = item.get('published_on')
        item['published_on'] = published_on.strftime(
            "%d-%m-%Y")
    return data


@frappe.whitelist(allow_guest=True)
def get_detail_post(name_section, name):
    try:
        doc_section = frappe.get_doc('Page Section', name_section)
        data = frappe.get_doc(doc_section.reference_document, name).as_dict()
        published_on = data.get('published_on')
        data['published_on'] = published_on.strftime(
            "%d-%m-%Y")
        return {'status': 200, 'data': data}
    except:
        return {'status': 0}


@frappe.whitelist(allow_guest=True)
def get_scroll_content_mobile_app(page, add_info=None, page_no=0, page_len=3):
    doc = frappe.get_doc('Web Page Builder', page)
    source_doc, sections, html = get_source_doc(doc, "Mobile")
    # hided by boopathy on 10/08/22
    # from ecommerce_business_store.ecommerce_business_store.api import get_all_restaurant_data, check_restaurant_distance
    # end
    start = int(page_no) * int(page_len)
    section_list = sections[int(start):int(int(page_len) + int(start))]
    sections_data = []
    data = get_page_section(source_doc)
    for item in section_list:
        data_source = next(
            (x for x in data if x.get('section') == item.section), None)
        allow = True
        if data_source.get('dynamic_data') == 1:
            if data_source['section_type'] in ['Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
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
        sections_data.append(data_source)
    return sections_data


@frappe.whitelist(allow_guest=True)
def get_scroll_content(page, device_type, add_info=None, page_no=0, page_len=3):
    doc = frappe.get_doc('Web Page Builder', page)
    # frappe.log_error(doc.as_dict(),">> Web page builder data <<")
    source_doc, sections, html = get_source_doc(doc, device_type)
    # frappe.log_error(source_doc,">> source_doc data <<")
    # frappe.log_error(list(sections),">> sections data <<")
    # frappe.log_error(html,">> hrml Template field name <<")
    html_list = []
    start = int(page_no) * int(page_len)
    if source_doc:
        html_list, js = get_page_html(
            doc=doc, sections=sections, html=html, source_doc=source_doc, device_type=device_type, add_info=add_info, page_no=start, page_len=int(page_len) + int(start))
    return html_list


@frappe.whitelist()
def upload_img():
    import base64
    # hide it boopathy on 10/08/22
    # from ecommerce_business_store.ecommerce_business_store.mobileapi import get_uploaded_file_content, update_doc
    # end
    files = frappe.request.files
    content = None
    filename = None
    img_type = frappe.form_dict.type
    dt = frappe.form_dict.doctype
    dn = frappe.form_dict.docname
    val = []
    if 'files[]' in files:
        file = files['files[]']
        content = file.stream.read()
        filename = file.filename
    if content:
        ret = frappe.get_doc({
            "doctype": "File",
            "attached_to_doctype": dt,
            "attached_to_name": dn,
            "folder": "Home",
            "file_name": filename,
            "is_private": 0,
            "content": content
        }).insert(ignore_permissions=True)
        return ret


@frappe.whitelist(allow_guest=True)
def get_random_images(dt, dn, business=None, ref_doc=None, image_option=None, image_docs=None):
    if not business:
        business = get_business_from_login()
    condition = ''
    if dt in ['Product', 'Product Category', 'Product Brand']:
        if business:
            condition = ' and p.restaurant = "{0}"'.format(business)
        if dt == "Product Category":
            products = frappe.db.sql_list(
                '''select p.name from `tabProduct Category Mapping` m inner join tabProduct p on p.name = m.parent where m.category = %(name)s {cond} group by p.name'''.format(cond=condition), {'name': dn})
        elif dt == "Product Brand":
            products = frappe.db.sql_list(
                '''select p.name from `tabProduct Brand Mapping` m inner join tabProduct p on p.name = m.parent where m.brand = %(name)s {cond} group by p.name'''.format(cond=condition), {'name': dn})
        elif dt == "Product":
            products = [dn]

        if products and len(products) > 0:
            product_list = ",".join(['"' + i + '"' for i in products])
            data = frappe.db.sql('''select list_image from `tabProduct Image` where parent in ({product}) order by is_primary desc limit 1'''.format(
                product=product_list), as_dict=1)
            if data and data[0].list_image:
                return data[0].list_image

    if ref_doc:
        if image_docs:
            docs = json.loads(image_docs)
            ref_field = next(
                (x['field_name'] for x in docs if x['document_name'] == ref_docs), None)
            if ref_field:
                if image_option == 'Child Table':
                    condition = ' where parent = "{0}"'.format(dn)
                else:
                    doc_meta = frappe.get_meta(dt, cached=True).fields
                    link_fields = next(
                        (x for x in doc_meta if x.options == ref_doc), None)
                    if link_fields:
                        ref_docs = frappe.db.sql_list('''select name from `tab{dt}` where {field} = "{val}"'''.format(
                            dt=ref_doc, field=link_fields.fieldname, val=dn))
                        if ref_docs:
                            condition = ' where name in ({0})'.format(
                                ', '.join([x for x in ref_docs]))

                if business:
                    condition += ' and business = "{0}"'.format(business)

                res = frappe.db.sql('''select {field} as image from `tab{dt}` {cond} order by rand()'''.format(
                    field=ref_field, dt=ref_doc, cond=condition), as_dict=True)
                if res and res[0].image:
                    return res[0].image

    media_settings = frappe.db.get_all(
        "Media Settings", fields=['default_image'])
    if media_settings:
        return media_settings[0].default_image


@frappe.whitelist()
def get_document_image(dt, dn, business=None):
    document_meta = frappe.get_meta(dt, cached=True).fields
    image_fields = list(filter(lambda x: x.fieldtype ==
                               'Attach Image', document_meta))
    if image_fields:
        return frappe.db.get_value(dt, dn, image_fields[0].fieldname)


@frappe.whitelist()
def update_page_data(doc, method):
    # update json data whenever changes occurs in any doctypes
    frappe.enqueue(
        "ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.update_json")


@frappe.whitelist()
def update_json():
    pages = frappe.db.sql_list(
        '''select name from `tabWeb Page Builder` where published = 1''')
    if pages:
        for item in pages:
            page = frappe.get_doc('Web Page Builder', item)
            page.save(ignore_permissions=True)


@frappe.whitelist()
def update_featured_item(name, checked, doctype="Product",  conditionfield="display_home_page"):
    if int(checked) == 1:
        frappe.db.set_value(doctype, name, conditionfield, 1)
        # 	eval(exec("doc.display_on_home_page = 1"))
    else:
        frappe.db.set_value(doctype, name, conditionfield, 0)
        # 	eval(exec("doc.display_on_home_page = 0"))
    doc = frappe.get_doc(doctype, name)
    # doc.save(ignore_permissions=True)
    return doc


@frappe.whitelist()
def get_featured_products():
    return frappe.db.get_all('Product', filters={'is_active': 1, 'display_home_page': 0}, fields=['*'])


@frappe.whitelist()
def get_collection_records(collections):
    try:
        if collections:
            items_list = frappe.db.sql(
                '''select product,product_name from `tabProduct Collection` where parent="{name}"'''.format(name=collections), as_dict=1)
            child_items = '""'
            if items_list:
                child_items = ",".join(
                    ['"' + x.product + '"' for x in items_list])
            query = '''SELECT doc.name, doc.item from `tabProduct` doc where doc.is_active = 1 and doc.name in ({0})'''.format(
                    child_items)
            result = frappe.db.sql(query, as_dict=1)
            return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(
        ), "ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.get_collection_records")
        return []


@frappe.whitelist()
def generate_page_html(page, view_type=None, page_type="Dynamic"):
    business = None
    page_template = ""
    builder = frappe.db.get_value("Web Page Builder", page, [
        "name", "business", "page_type", "route", "published", "custom_js", "custom_css", "document"], as_dict=True)
    if page_type == "Dynamic":
        page_template += '{% extends layout_template %}\n\t{% block loader %}\n\t\t{% endblock %}\n{% block title %}\n{% if meta_title %}{{meta_title}}{% else %}{{title}}{% endif %}\n{% endblock %}\n{% block content %}\n<div class="builder-section">'
    else:
        page_template += '{% extends layout_template %}\n\t{% block loader %}\n\t\t{% endblock %}\n{% block content %}\n<div class="builder-section">\n'
    if builder:
        business = None
        if builder.business:
            business = builder.business
        else:
            business = "custom_html"
        component = frappe.db.get_all('Mobile Page Section', fields=['section', 'name', 'section_title', 'section_name', 'section_type', 'content_type', 'route'], filters={
            'parent': builder.name, 'parentfield': 'web_section'}, order_by='idx')

        if not builder.document:
            component = component[0:3]
        if len(component) > 0:
            for item in component:
                homepagedata = frappe.db.get_all(
                    'Page Section', fields=['*'], filters={'name': item.section})[0]
                if homepagedata:
                    section_name = homepagedata.section_title.lower().replace(
                        ' ', '-') + "-" + (homepagedata.name).lower().replace(' ', '-')
                    page_template += '{% include "templates/pages/' + \
                        business+'/'+section_name+'.html" %}\n'
        page_template += '\n</div>\n'

    if builder.custom_css:
        context = {}
        page_template += '<style>\n'
        css_template = frappe.render_template(builder.custom_css, context)
        page_template += css_template
        page_template += '\n</style>\n'
    page_template += '{% endblock %}\n'

    if builder.custom_js:
        page_template += '{% block script %}\n'
        page_template += '<script type="text/javascript">\n'
        page_template += default_page_script
        context = {}
        js_template = frappe.render_template(builder.custom_js, context)
        page_template += js_template
        page_template += '\n</script>\n'
        page_template += '{% endblock %}\n'

    return page_template


@frappe.whitelist(allow_guest=True)
def get_page_content(page, device_type, page_no=0, page_len=3):
    doc = frappe.get_doc('Web Page Builder', page)
    source_doc, sections = get_source_doc_data(doc, device_type)
    data_list = []
    start = int(page_no) * int(page_len)
    if source_doc:
        data_list = get_page_data(
            doc, sections, source_doc, device_type, start, int(page_len) + int(start))
    return data_list


@frappe.whitelist()
def get_element_properties(id):
    fields = frappe.db.get_all("Section Content", filters={"name": id}, fields=[
        "css_json", "field_type", "parent", "field_key"])
    css_properties = frappe.db.get_all("Field Types Property", filters={
        "field_type": fields[0].field_type}, fields=['css_properties_list'])
    if css_properties:
        fields[0].css_properties_list = css_properties[0].css_properties_list
        class_name = frappe.db.get_value(
            "Page Section", fields[0].parent, "class_name")
        if not class_name:
            class_name = get_class_name()
            # modified by boopathy on 10/08/2022
            # from ecommerce_business_store.cms.doctype.page_section.page_section import get_class_name
            from go1_cms.go1_cms.doctype.page_section.page_section import get_class_name
            # end
            page_section_doc = frappe.get_doc("Page Section", fields[0].parent)
            page_section_doc.class_name = class_name
            page_section_doc.save()
        fields[0].class_name = class_name
    fonts_list = frappe.db.get_all("CSS Font", fields=['name', 'font_family'])
    fields[0].fonts_list = fonts_list
    return fields[0]


@frappe.whitelist()
def get_section_element_properties(id):
    fields = frappe.db.get_all("Section Content", filters={"name": id}, fields=[
        "css_json", "field_type", "parent", "field_key"])
    css_properties = frappe.db.get_all("Field Types Property", filters={
        "field_type": fields[0].field_type}, fields=['css_properties_list'])
    if css_properties:
        fields[0].css_properties_list = css_properties[0].css_properties_list
    fonts_list = frappe.db.get_all("CSS Font", fields=['name', 'font_family'])
    fields[0].fonts_list = fonts_list
    return fields[0]


@frappe.whitelist(allow_guest=True)
def get_context_content(route, context=None, page_no=0, page_len=3):
    page_builder = frappe.get_doc('Web Page Builder', {"route": route})
    page_section = frappe.get_all("Mobile Page Section", fields=["name", "section", "parent"], filters={
        "parent": page_builder.name, 'parentfield': 'web_section'}, order_by='idx')
    context['section_len'] = len(page_section)
    # frappe.log_error(len(page_section), "-----context------")
    page_section = page_section[int(page_no):int(page_len)]
    for item in page_section:
        data = get_section_data(item.section, item.parent, context.device_type)
        if data:
            context[data['context']] = {}
            for key, value in data.items():
                context[data['context']][key] = value


def get_source_doc_data(doc, device_type):
    source_doc = sections = None
    if device_type == 'Desktop':
        view_type = 'web'
        sections = doc.web_section
    elif device_type == 'Mobile':
        view_type = 'mobile'
        sections = doc.mobile_section if doc.page_type == 'Adaptive' else doc.web_section
    if doc.page_type == 'Responsive':
        source_doc = 'data_source/{0}_web.json'.format(
            doc.name.lower().replace(' ', '_'))
    else:
        source_doc = 'data_source/{0}_{1}.json'.format(
            doc.name.lower().replace(' ', '_'), (view_type if view_type else None))

    return source_doc, sections


def get_query_condition(user):
    if "Admin" in frappe.get_roles(frappe.session.user) and not "Administrator" in frappe.get_roles(frappe.session.user):
        return "(`tabWeb Page Builder`.document is NULL)"


@frappe.whitelist()
def get_shuffled_category_products(category, no_of_records):
    # hided by boopathy-10/08/2022
    # from ecommerce_business_store.ecommerce_business_store.api import get_child_categories
    # end
    catalog_settings = None
    if 'erp_ecommerce_business_store' in frappe.get_installed_apps():
        from erp_ecommerce_business_store.utils.setup import get_settings_from_domain
        catalog_settings = get_settings_from_domain('Catalog Settings')
        from ecommerce_business_store.ecommerce_business_store.api import get_child_categories
    if 'ecommerce_business_store' in frappe.get_installed_apps():
        from ecommerce_business_store.utils.setup import get_settings_from_domain
        catalog_settings = get_settings_from_domain('Catalog Settings')
        from ecommerce_business_store.ecommerce_business_store.v2.category import get_child_categories
    # catalog_settings = get_settings_from_domain('Catalog Settings')
    category_filter = ""
    sort = "ORDER BY RAND()"
    conditions = ""
    if category:
        category_filter = "'" + category + "'"
    if catalog_settings.include_products_from_subcategories == 1:
        child_categories = get_child_categories(category)
        if child_categories:
            category_filter = ','.join(
                ['"' + x.name + '"' for x in child_categories])
    books_join_query = ''
    books_columns_query = ''
    installed_apps = frappe.db.sql(
        ''' select * from `tabModule Def` where app_name='book_shop' ''', as_dict=True)
    if len(installed_apps) > 0:
        books_columns_query = ',AU.author_name,AU.route as author_route,PU.publisher_name,PU.route as publisher_route'
        books_join_query = '  left join `tabAuthor` AU on AU.name=p.author left join `tabPublisher` PU on PU.name=p.publisher'
    query = "select distinct p.item,p.restaurant,p.price,p.old_price,p.short_description,p.tax_category,p.full_description,p.sku,p.name,p.route,p.inventory_method,p.is_gift_card,(case when inventory_method ='Track Inventory' then p.stock else  10000 end) as stock,p.minimum_order_qty,p.maximum_order_qty,p.disable_add_to_cart_button,p.enable_preorder_product,p.weight,p.gross_weight,p.approved_total_reviews,CM.category,\
	pc.show_attributes_inlist,pc.products_per_row_for_mobile_app,\
								(select list_image from `tabProduct Image` where parent=p.name order by is_primary desc limit 1) as product_image,\
								(select brand_name from `tabProduct Brand Mapping` where parent=p.name limit 1) as product_brand,\
								(select B.route from `tabProduct Brand Mapping` MP\
								inner join `tabProduct Brand` B on MP.brand=B.name\
								where MP.parent=p.name and B.published=1 limit 1) as brand_route" \
            + books_columns_query + ' from `tabProduct` p ' + books_join_query \
            + " inner join `tabProduct Category Mapping` CM on CM.parent=p.name\
		inner join `tabProduct Category` pc on CM.category=pc.name\
								where p.is_active=1 and p.status='Approved' and CM.category in(%s) %s group by p.name %s limit %d,%d " \
            % (category_filter, conditions, sort, 0, int(no_of_records))
    # update by kartheek for getting author and publisher on 19-08-2019
    result = frappe.db.sql(query, as_dict=True)
    return result


@frappe.whitelist()
def import_sections_from_template(page_id, id_client_website=''):
    page_template = frappe.get_doc("Page Template", page_id)
    mobile_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": page_id, "parentfield": "mobile_section"}, fields=[
        'section', 'section_title', 'section_type', 'content_type', 'allow_update_to_style'], order_by="idx")
    web_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": page_id, "parentfield": "web_section"}, fields=[
        'section', 'section_title', 'section_type', 'content_type', 'allow_update_to_style'], order_by="idx")
    mobile_secs = []
    web_secs = []
    for x in mobile_sections:
        target_doc = None
        doc = frappe.new_doc("Page Section")
        doc = get_mapped_doc("Page Section", x.section,	{
            "Page Section": {
                "doctype": "Page Section"
            },
        }, target_doc, ignore_permissions=True)
        if doc.section_type == "Form" and doc.form:
            target_doc_form = None
            doc_form = frappe.new_doc("MBW Form")
            doc_form = get_mapped_doc("MBW Form", doc.form,	{
                "MBW Form": {
                    "doctype": "MBW Form"
                },
            }, target_doc_form, ignore_permissions=True)
            doc_form.id_client_website = id_client_website
            doc_form.id_parent_copy = doc.form
            doc_form.save(ignore_permissions=True)
            # set new id form
            doc.form = doc_form.name
        doc.save(ignore_permissions=True)
        m_page_sec = frappe.new_doc("Mobile Page Section")
        m_page_sec.section_title = x.section_title
        m_page_sec.section_type = x.section_type
        m_page_sec.content_type = x.content_type
        m_page_sec.allow_update_to_style = x.allow_update_to_style
        m_page_sec.parentfield = "mobile_section"
        m_page_sec.parenttype = "Web Page Builder"
        m_page_sec.section = doc.name
        mobile_secs.append(m_page_sec)
    for x in web_sections:
        target_doc = None
        doc = frappe.new_doc("Page Section")
        doc = get_mapped_doc("Page Section", x.section,	{
            "Page Section": {
                "doctype": "Page Section"
            },
        }, target_doc, ignore_permissions=True)
        if doc.section_type == "Form" and doc.form:
            form_set = frappe.db.get_value(
                'MBW Form', {'id_parent_copy': doc.form}, ['name'], as_dict=1)
            if not form_set:
                target_doc_form = None
                doc_form = frappe.new_doc("MBW Form")
                doc_form = get_mapped_doc("MBW Form", doc.form,	{
                    "MBW Form": {
                        "doctype": "MBW Form"
                    },
                }, target_doc_form, ignore_permissions=True)
                doc_form.id_client_website = id_client_website
                doc_form.id_parent_copy = doc.form
                doc_form.save(ignore_permissions=True)
                form_set_name = doc_form.name
            else:
                form_set_name = form_set.name
            # set new id form
            doc.form = form_set_name
        doc.save(ignore_permissions=True)
        m_page_sec = frappe.new_doc("Mobile Page Section")
        m_page_sec.section_title = x.section_title
        m_page_sec.section_type = x.section_type
        m_page_sec.content_type = x.content_type
        m_page_sec.allow_update_to_style = x.allow_update_to_style
        m_page_sec.parentfield = "web_section"
        m_page_sec.parenttype = "Web Page Builder"
        m_page_sec.section = doc.name
        web_secs.append(m_page_sec)
    return {"web_sections": web_secs, "mobile_sections": mobile_secs, "info": page_template}


@frappe.whitelist()
def save_as_template(page_id, title):
    from frappe.model.mapper import get_mapped_doc
    web_page = frappe.get_doc("Web Page Builder", page_id)
    page_template = frappe.new_doc("Page Template")
    page_template_doc = None
    page_template = get_mapped_doc("Web Page Builder", page_id,	{
        "Web Page Builder": {
            "doctype": "Page Template"
        },
    }, page_template_doc, ignore_permissions=True)
    page_template.page_title = title
    page_template.save(ignore_permissions=True)
    mobile_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": page_id, "parentfield": "mobile_section"}, fields=[
        'idx', 'section', 'section_title', 'section_type', 'content_type', 'allow_update_to_style'], order_by="idx")
    web_sections = frappe.db.get_all("Mobile Page Section", filters={"parent": page_id, "parentfield": "web_section"}, fields=[
        'idx', 'section', 'section_title', 'section_type', 'content_type', 'allow_update_to_style'], order_by="idx")
    mobile_secs = []
    web_secs = []
    for x in mobile_sections:
        target_doc = None
        doc = frappe.new_doc("Page Section")
        doc = get_mapped_doc("Page Section", x.section,	{
            "Page Section": {
                "doctype": "Page Section"
            },
        }, target_doc, ignore_permissions=True)
        doc.save(ignore_permissions=True)
        m_page_sec = frappe.new_doc("Mobile Page Section")
        m_page_sec.section_title = x.section_title
        m_page_sec.section_type = x.section_type
        m_page_sec.content_type = x.content_type
        m_page_sec.allow_update_to_style = x.allow_update_to_style
        m_page_sec.parent = page_template.name
        m_page_sec.parentfield = "mobile_section"
        m_page_sec.parenttype = "Page Template"
        m_page_sec.section = doc.name
        m_page_sec.idx = x.idx
        mobile_secs.append(m_page_sec)
    for x in web_sections:
        target_doc = None
        doc = frappe.new_doc("Page Section")
        doc = get_mapped_doc("Page Section", x.section,	{
            "Page Section": {
                "doctype": "Page Section"
            },
        }, target_doc, ignore_permissions=True)
        doc.save(ignore_permissions=True)
        m_page_sec = frappe.new_doc("Mobile Page Section")
        m_page_sec.section_title = x.section_title
        m_page_sec.section_type = x.section_type
        m_page_sec.content_type = x.content_type
        m_page_sec.allow_update_to_style = x.allow_update_to_style
        m_page_sec.parent = page_template.name
        m_page_sec.parentfield = "web_section"
        m_page_sec.parenttype = "Page Template"
        m_page_sec.section = doc.name
        m_page_sec.idx = x.idx
        web_secs.append(m_page_sec)
    page_template.mobile_section = mobile_secs
    page_template.web_section = web_secs
    page_template.save(ignore_permissions=True)
    web_page.is_converted_to_template = 1
    web_page.save(ignore_permissions=True)
    return "success"


@frappe.whitelist()
def get_shuffled_blog_category(category, no_of_records):
    category_filter = ""
    sort = "ORDER BY RAND()"
    if category:
        category_filter = "'" + category + "'"
    query = "select distinct * from `tabBlog Post` p where p.published=1 and p.blog_category in(%s) group by p.name %s limit %d,%d " \
            % (category_filter, sort, 0, int(no_of_records))
    # update by kartheek for getting author and publisher on 19-08-2019
    result = frappe.db.sql(query, as_dict=True)
    return result


def get_page_data(doc, sections, source_doc, device_type, page_no=0, page_len=5):
    section_list = sections[int(page_no):int(page_len)]
    data = get_page_section(source_doc)
    data_list = []
    for item in section_list:
        data_source = next(
            (x for x in data if x.get('section') == item.section), None)
        allow = True
        if data_source.get('dynamic_data') == 1:
            if data_source['section_type'] in ['Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
                pg_doc = frappe.get_doc('Page Section', data_source['section'])
                data_source = pg_doc.run_method('section_data')
            if data_source.get('login_required') == 1:
                if frappe.session.user != 'Guest':
                    # modified by boopathy - 10/08/2022
                    # from ecommerce_business_store.cms.doctype.page_section.page_section import get_data_source
                    from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source

                    # end
                    doc = frappe.get_doc('Page Section', item.section)
                    data_source['data'] = get_data_source(
                        doc.query, doc.reference_document, doc.no_of_records, 1, business=doc.business)
                else:
                    allow = False
            if allow:
                catalog_settings = get_settings_from_domain('Catalog Settings')
                general_settings = get_settings_from_domain('Business Setting')
                # theme_settings =  get_settings_from_domain('Web Theme')
                # theme = get_theme_settings()
                currency = frappe.cache().hget('currency', 'symbol')
                data_source['catalog_settings'] = catalog_settings
                # data_source['theme_settings'] = theme_settings
                data_source['general_settings'] = general_settings
                data_source['currency'] = currency
                data_source['device_type'] = device_type
                product_box = catalog_settings.product_boxes

                if product_box:
                    data_source['product_box'] = frappe.db.get_value(
                        'Product Box', product_box, 'route')
                try:
                    data_list.append(
                        {'data_source': data_source, 'section': item.section})
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(
                    ), "ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.get_page_html")
    return data_list


default_page_script = """<script>
	$(document).ready(function() {
  var page_no = 0;
  var page_len = 3;
  var section_len = {{ section_len }};
  var scroll = false;
  var ecommerce_baseurl = '/api/method/ecommerce_business_store.cms.';
  var path = window.location.pathname
  path = path.replace("/", "")
  path = path.split('/');
  var route = path[0]
  $(window).scroll(function() {
	  if (scroll == false) {
		  scroll = true;
		  var url = ecommerce_baseurl + 'api.get_scroll_content'
		  get_scroll_data_forbuilder(url, route)
	  }
  })

  function get_scroll_data_forbuilder(url, route) {
	  try {
		  $('.loader').css("display", "none")
		  page_no = page_no + 1;
		  var start = parseInt(page_no) * parseInt(page_len)
		  if (start < section_len) {
			  $.ajax({
				  type: 'POST',
				  Accept: 'application/json',
				  ContentType: 'application/json;charset=utf-8',
				  url: window.location.origin + url,
				  data: {
					  'page_no': page_no,
					  'page_len': page_len,
					  'route': route,
					  'device_type': device_type
				  },
				  dataType: "json",
				  async: false,
				  headers: {
					  'X-Frappe-CSRF-Token': frappe.csrf_token
				  },
					success: function(data) {
						if (parseInt((page_no)) * parseInt(page_len) >= 100) {
							$('.load-more').show();
							scroll = true;
						} else {
						   scroll = false;
						   $('.load-more').hide();
						}
						if (data.message) {
							setTimeout(function() {
								$('.page-section').find('div:eq(1)').find('.loader').css("display", "none");
								$('.page-section').find('div:eq(1)').append(data.message)
							}, 9000);

						} else {
							$('.load-more').hide();
						}
					}
				})
			}
		} catch (e) {
			logging_the_error(e, "builder.get_scroll_data_forbuilder");
		}
	}
});
</script>\n"""


# added by boopathy


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

# @frappe.whitelist(allow_guest=True)
# def get_bestsellers(business=None, limit=None, isMobile=0):
# 	try:
# 		if not limit:
# 			limit = catalog_settings.no_of_best_sellers
# 		if catalog_settings.display_best_seller_products:

# 			# updated by kartheek for getting author and publisher on 19-08-2019

# 			books_join_query = ''
# 			books_columns_query = ''
# 			installed_apps = frappe.db.sql(''' select * from `tabModule Def` where app_name='book_shop' ''', as_dict=True)
# 			if len(installed_apps) > 0:
# 				books_columns_query = ',AU.author_name,AU.route as author_route,PU.publisher_name,PU.route as publisher_route'
# 				books_join_query = '  left join `tabAuthor` AU on AU.name=p.author left join `tabPublisher` PU on PU.name=p.publisher'
# 			condition = ''
# 			if business:
# 				condition += ' and p.restaurant = "{0}"'.format(business)
# 			query = "select p.item,p.tax_category,p.price,p.old_price,p.short_description,p.full_description,p.sku,p.name,p.route,p.inventory_method,p.minimum_order_qty,p.maximum_order_qty,p.stock,p.disable_add_to_cart_button,p.restaurant,\
# 				(select list_image from `tabProduct Image` i where parent=p.name order by is_primary desc\
# 				limit 1) as product_image, (select detail_thumbnail from `tabProduct Image` i where parent=p.name order by is_primary desc\
# 				limit 1) as detail_thumbnail,(select brand_name from `tabProduct Brand Mapping` where parent=p.name\
# 				limit 1) as product_brand,\
# 				(select B.route from `tabProduct Brand Mapping` MP\
# 									inner join `tabProduct Brand` B on MP.brand=B.name\
# 									where MP.parent=p.name and B.published=1 limit 1) as brand_route,\
# 				sum(oi.quantity) as qty " + books_columns_query + " from `tabProduct` p inner join `tabOrder Item` oi\
# 				on oi.item=p.name " + books_join_query + ' where p.is_active=1 ' + condition \
# 				+ ' group by p.name order by qty desc limit ' + str(limit)
# 			Items = frappe.db.sql(query, as_dict=True)

# 			# Items=frappe.db.sql('''select p.item,p.tax_category,p.price,p.old_price,p.short_description,p.full_description,p.sku,p.name,p.route,p.inventory_method,p.minimum_order_qty,p.maximum_order_qty,p.stock,
# 			#   (select list_image from `tabProduct Image` i where parent=p.name order by is_primary desc
# 			#   limit 1) as product_image, (select detail_thumbnail from `tabProduct Image` i where parent=p.name order by is_primary desc
# 			#   limit 1) as detail_thumbnail,(select brand_name from `tabProduct Brand Mapping` where parent=p.name
# 			#   limit 1) as product_brand,
# 			#   (select B.route from `tabProduct Brand Mapping` MP
# 			#                       inner join `tabProduct Brand` B on MP.brand=B.name
# 			#                       where MP.parent=p.name and B.published=1 limit 1) as brand_route,
# 			#   sum(oi.quantity) as qty %(books_columns_query)s from `tabProduct` p inner join `tabOrder Item` oi
# 			#   on oi.item=p.name %(books_join_query)s where p.is_active=1 group by p.name order by qty desc limit %(limit)s''',{'limit':limit,'books_columns_query':books_columns_query,'books_join_query':books_join_query},as_dict=1)
# 			# updated by kartheek for getting author and publisher on 19-08-2019

# 			if Items:
# 				Items = get_product_details(Items, isMobile)
# 			return Items
# 		else:
# 			return []
# 	except Exception:
# 		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store.ecommerce_business_store.api.get_bestsellers')


# def get_product_price(product, qty=1, rate=None,attribute_id=None, customer=None):
# 	try:
# 		web_type = None
# 		try:
# 			domain = frappe.get_request_header('host')
# 			if domain and check_domain('saas'):
# 				business = get_business_from_web_domain(domain)
# 				web_type = 'Website' if business else 'Marketplace'
# 		except Exception as e:
# 			pass
# 		if isinstance(attribute_id, list):
# 			if len(attribute_id)==1:
# 				attribute_id = attribute_id[0]
# 		# price = product.price
# 		cust = customer
# 		if frappe.request:
# 			cust = frappe.request.cookies.get('customer_id')
# 		# price=price-get_product_discount_amount(product)
# 		cart_items=None
# 		if cust:
# 			cart = frappe.db.exists("Shopping Cart", {"customer": cust})
# 			if cart:
# 				doc = frappe.get_doc("Shopping Cart", cart)
# 				cart_items = ','.join('"{0}"'.format(r.product) for r in doc.items)
# 		#hide it by boopathy - 10/08/22
# 		# from ecommerce_business_store.ecommerce_business_store.doctype.discounts.discounts import get_product_discount
# 		#end
# 		res = get_product_discount(product, qty, rate, customer_id=customer, website_type=web_type, attribute_id=attribute_id, product_array=cart_items)
# 		return res
# 	except Exception:
# 		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store.ecommerce_business_store.api.get_product_price')


# @frappe.whitelist(allow_guest=True)
# def get_category_products(category=None, sort_by=None, page_no=1, page_size=no_of_records_per_page,
# 	brands=None, rating=None, min_price=None, max_price=None, attributes=None, as_html=None,
# 	productsid=None, view_by=None, isMobile=0, domain=None, models=None, onlybrand_finder=0, customer=None,route=None,business_id=None):
# 	try:
# 		if route:
# 			categories = frappe.db.get_all("Product Category",filters={"route":route})
# 			if categories:
# 				category = categories[0].name
# 		catalog_settings = get_settings_from_domain('Catalog Settings', domain=domain)
# 		default_sort_order = get_settings_value_from_domain('Catalog Settings',	'default_product_sort_order', domain=domain)
# 		sort_order = get_sorted_columns(default_sort_order)
# 		if sort_by:
# 			sort_order = sort_by
# 		category_products = get_sorted_category_products(category, sort_order, page_no, page_size,
# 			brands, rating, min_price, max_price, attributes, productsid, domain=domain, models=models, onlybrand_finder=onlybrand_finder,business_id=business_id)
# 		if category_products:
# 			category_products = get_product_details(category_products, isMobile, customer=customer, current_category=category)
# 			theme = get_theme_settings(domain)
# 			product_box = None
# 			if theme:
# 				product_box = frappe.db.get_value('Web Theme', theme, 'grid_product_box')
# 			if not product_box:
# 				product_box = catalog_settings.product_boxes
# 			if as_html and product_box:
# 				product_box_view = frappe.db.get_value('Product Category',category,'default_view')
# 				category_product_box = frappe.db.get_value('Product Category',category,'product_box_for_list_view')
# 				if product_box_view and product_box_view == "List View":
# 					if theme and frappe.db.get_value('Web Theme', theme, 'list_product_box'):
# 						product_box = frappe.db.get_value('Web Theme', theme, 'list_product_box')
# 					elif catalog_settings.list_view_product_box:
# 						product_box = catalog_settings.list_view_product_box
# 				if category_product_box:
# 					product_box = category_product_box
# 				file_name = frappe.db.get_value('Product Box', product_box, 'route')
# 				template = frappe.get_template(file_name)
# 				currency = frappe.cache().hget('currency', 'symbol')
# 				return template.render({'products': category_products, 'currency': currency, 'catalog_settings': catalog_settings})
# 		return category_products
# 	except Exception:
# 		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store.ecommerce_business_store.api.get_category_products')


# @frappe.whitelist(allow_guest=True)
# def get_category_detail(product_name):
# 	cur_category = frappe.db.sql('''select PC.category from `tabProduct`p inner join `tabProduct Category Mapping`PC  where p.name=%(name)s and PC.parent=p.name'''
# 					  , {'name': product_name}, as_dict=1)
# 	if cur_category:
# 		for cat in cur_category:
# 			get_cat = frappe.db.sql('''select parent_product_category,product_info from `tabProduct Category` where name=%(name)s''', {'name': cat.category}, as_dict=1)
# 			if get_cat[0]['product_info'] != '':
# 				return get_cat[0]['product_info']
# 			else:
# 				if get_cat[0]['parent_product_category']:
# 					get_cat1 = frappe.db.sql('''select parent_product_category,product_info from `tabProduct Category` where name=%(name)s''', {'name': get_cat[0]['parent_product_category']}, as_dict=1)
# 					if get_cat1[0]['product_info'] != '':
# 						return get_cat1[0]['product_info']
# 					else:
# 						if get_cat1[0]['parent_product_category']:
# 							get_cat2 = frappe.db.sql('''select parent_product_category,product_info from `tabProduct Category` where name=%(name)s''',{'name': get_cat1[0]['parent_product_category']}, as_dict=1)
# 							if get_cat2[0]['product_info'] != '':
# 								return get_cat2[0]['product_info']


# @frappe.whitelist(allow_guest=True)
# def get_enquiry_product_detail(product_id):
# 	cur_category = frappe.db.sql('''select PC.category from `tabProduct`p inner join `tabProduct Category Mapping`PC  where p.name=%(name)s and PC.parent=p.name''', {'name': product_id}, as_dict=1)
# 	if cur_category:
# 		for cat in cur_category:
# 			get_cat = frappe.db.sql('''select parent_product_category,type_of_category from `tabProduct Category` where name=%(name)s''', {'name': cat.category}, as_dict=1)
# 			if get_cat[0]['type_of_category'] == 'Enquiry Product':
# 				return get_cat[0]['type_of_category']
# 			else:
# 				if get_cat[0]['parent_product_category']:
# 					get_cat1 = frappe.db.sql('''select parent_product_category,type_of_category from `tabProduct Category` where name=%(name)s''',{'name': get_cat[0]['parent_product_category']}, as_dict=1)
# 					if get_cat1[0]['type_of_category'] == 'Enquiry Product':
# 						return get_cat1[0]['type_of_category']
# 					else:
# 						if get_cat1[0]['parent_product_category']:
# 							get_cat2 = frappe.db.sql('''select parent_product_category,type_of_category from `tabProduct Category` where name=%(name)s''',{'name': get_cat1[0]['parent_product_category']}, as_dict=1)
# 							if get_cat2[0]['type_of_category'] == 'Enquiry Product':
# 								return get_cat2[0]['type_of_category']
# 							else:
# 								return get_cat2[0]['type_of_category']
# 						else:
# 							return get_cat1[0]['type_of_category']
# 				else:
# 					return get_cat[0]['type_of_category']


# @frappe.whitelist(allow_guest=True)
# def get_customer_recently_viewed_products(customer=None, domain=None, isMobile=0,business=None):
# 	products = []
# 	if not customer:
# 		if frappe.request.cookies.get('customer_id'):
# 			customer = unquote(frappe.request.cookies.get('customer_id'))
# 	catalog_settings = get_settings_from_domain('Catalog Settings')
# 	if customer and catalog_settings.enable_recetly_viewed_products:
# 		cond = ''
# 		if domain:
# 			business = get_business_from_web_domain(domain)
# 			if business:
# 				cond = ' and p.restaurant = "{0}"'.format(business)
# 		if business:
# 			cond = ' and p.restaurant = "{0}"'.format(business)

# 		# recently_viewed_products = frappe.get_all("Customer Viewed Product",fields=['product'],filters={'parent':customer},order_by="viewed_date desc")

# 		recently_viewed_products = frappe.db.sql('''select c.product from `tabCustomer Viewed Product` c inner join tabProduct p on p.name = c.product where c.parent = %(parent)s {cond} order by viewed_date desc'''.format(cond=cond),{'parent': customer}, as_dict=1)
# 		books_join_query = ''
# 		books_columns_query = ''
# 		conditions = ''
# 		if recently_viewed_products:
# 			conditions += ' and p.name in('
# 		installed_apps = frappe.db.sql(''' select * from `tabModule Def` where app_name='book_shop' ''', as_dict=True)
# 		for x in recently_viewed_products:
# 			conditions += "'" + x.product + "',"
# 		if recently_viewed_products:
# 			conditions = conditions[:-1]
# 			conditions += ' )'
# 		if cond:
# 			conditions += cond
# 		if len(installed_apps) > 0:
# 			books_columns_query = ',AU.author_name,AU.route as author_route,PU.publisher_name,PU.route as publisher_route'
# 			books_join_query = '  left join `tabAuthor` AU on AU.name=p.author left join `tabPublisher` PU on PU.name=p.publisher'

# 		query = "select p.item,p.restaurant,p.price,p.old_price,p.short_description,p.tax_category,p.full_description,p.sku,p.name,p.route,p.inventory_method,p.stock,p.minimum_order_qty,p.maximum_order_qty,p.disable_add_to_cart_button,CM.category,\
# 									(select list_image from `tabProduct Image` where parent=p.name order by is_primary desc limit 1) as product_image,\
# 									(select brand_name from `tabProduct Brand Mapping` where parent=p.name limit 1) as product_brand,\
# 									(select B.route from `tabProduct Brand Mapping` MP\
# 									inner join `tabProduct Brand` B on MP.brand=B.name\
# 									where MP.parent=p.name and B.published=1 limit 1) as brand_route" \
# 			+ books_columns_query + ' from `tabProduct` p ' \
# 			+ books_join_query \
# 			+ " inner join `tabProduct Category Mapping` CM on CM.parent=p.name\
# 									where p.is_Active=1 and p.status='Approved'  %s group by p.name limit %d" \
# 			% (conditions, 12)
# 		products = frappe.db.sql(query, as_dict=True)

# 		# for thumbnails by Rajeshwari on 13-12-19

# 		if products:
# 			products = get_product_details(products, isMobile=isMobile)

# 	return products


# @frappe.whitelist(allow_guest=True)
# def get_product_other_info(item, domain=None, isMobile=0, business=None,customer=None):
# 	'''
# 		To get additional product information to show in product detail page

# 		param: item: product id
# 	'''
# 	if domain:
# 		business = None
# 		business = get_business_from_web_domain(domain)

# 	customer_bought = best_sellers = related_products = related_categories = cross_selling_products= []
# 	categories_list = frappe.db.sql('''select category, category_name, (select route from `tabProduct Category` c where c.name = pcm.category) as route from `tabProduct Category Mapping` pcm where parent = %(parent)s order by idx limit 1''', {'parent': item}, as_dict=1)
# 	catalog_settings = get_settings_from_domain('Catalog Settings')
# 	recently_viewed_products =[]
# 	if catalog_settings.customers_who_bought:
# 		customer_bought = get_products_bought_together(item, business=business, isMobile=isMobile)
# 	if catalog_settings.enable_best_sellers:
# 		if categories_list and categories_list[0].category:
# 			best_sellers = get_category_based_best_sellers(categories_list[0].category, item, business=business, isMobile=isMobile)
# 	mapped_related_categories = frappe.db.get_all("Related Product Category",filters={"parent":item},fields=['category'])
# 	# frappe.log_error(mapped_related_categories,'mapped_related_categories')
# 	if catalog_settings.enable_related_products:
# 		if categories_list:
# 			mapped_related_products = frappe.db.get_all("Related Product",filters={"parent":item},fields=['product'])
# 			if not mapped_related_products:
# 				related_products = get_category_products(categories_list[0].category, productsid=item, page_size=18, domain=domain, isMobile=isMobile,customer=customer)
# 			else:
# 				if mapped_related_products:
# 					check_related_products = []
# 					for x in mapped_related_products:
# 						product = frappe.db.get_all("Product",filters={"name":x.product},fields=['*'])
# 						if product:
# 							product_images = frappe.db.sql("""select list_image from `tabProduct Image` where parent=%(product_id)s order by is_primary desc limit 1""",{"product_id":x.product},as_dict=1)
# 							if product_images:
# 								product[0].product_image = product_images[0].list_image
# 							check_related_products.append(product[0])
# 					related_products = get_product_details(check_related_products)
# 	# if  mapped_related_categories:
# 		# related_categories = get_multiple_category_products(mapped_related_categories,page_size=18)
# 	related_categories = get_related_categories(mapped_related_categories)
# 	#updated by boopathy
# 	if catalog_settings.enable_cross_selling_products:
# 		cross_selling_items = frappe.get_list("Cross Selling Products",fields={"product"},filters={"parent":item})
# 		if cross_selling_items:
# 			for o in cross_selling_items:
# 				product = frappe.get_list("Product",filters={"name":o['product']},fields=['*'])
# 				res_data = get_product_details(product)
# 				if res_data:
# 					cross_selling_products.append(res_data[0])
# 	recommended_products = []
# 	# if catalog_settings.enable_recommended_products:

# 	# 	viewed_items = []
# 	# 	if customer:
# 	# 		cond = " where o.customer='{customer}'""".format(customer=customer)
# 	# 		viewed_query = """select distinct product from `tabCustomer Viewed Product` where parent ='{customer}'""".format(customer=customer)
# 	# 		viewed_items = frappe.db.sql(viewed_query, as_dict=True)
# 	# 	else:
# 	# 		cond = ""
# 	# 	orderquery = """select MAX(i.item) as product from `tabOrder` o inner join `tabOrder Item` i ON i.parent=o.name  {cond}""".format(cond=cond)
# 	# 	order_items = frappe.db.sql(orderquery, as_dict=True)
# 	# 	for s in order_items:
# 	# 		s.price = frappe.db.get_value("Product", s.product, "price")
# 	# 	cartquery = """select i.product, i.price from `tabShopping Cart` o inner join `tabCart Items` i ON i.parent=o.name  {cond}""".format(cond=cond)
# 	# 	cart_items = frappe.db.sql(cartquery, as_dict=True)

# 	# 	for n in cart_items:
# 	# 		order_items.append(n)

# 	# 	for s in viewed_items:
# 	# 		order_items.append(s)

# 	# 	recommended_item_list = []
# 	# 	recommended_item_list=",".join(['"' + x.product + '"' for x in order_items])
# 	# 	catquery = """select distinct category from `tabProduct Category Mapping` where parent in ({lists})""".format(lists=recommended_item_list)
# 	# 	cat_items = frappe.db.sql(catquery, as_dict=True)
# 	# 	max_val = max(flt(node.price) for node in order_items)
# 	# 	min_val = min(flt(node.price) for node in order_items)
# 	# 	category_list = []
# 	# 	category_list=",".join(['"' + x.category + '"' for x in cat_items])
# 	# 	if category_list:
# 	# 		ord_query = """select p.* from `tabProduct` p inner join `tabProduct Category Mapping` pc on pc.parent=p.name where pc.category in ({category_list}) and p.price >='{min_val}' and p.price <='{max_val}'""".format(lists=recommended_item_list, category_list=category_list,min_val=min_val, max_val=max_val)
# 	# 	else:
# 	# 		ord_query = """select p.* from `tabProduct` p inner join `tabProduct Category Mapping` pc on pc.parent=p.name where  p.price >='{min_val}' and p.price <='{max_val}'""".format(lists=recommended_item_list, category_list=category_list,min_val=min_val, max_val=max_val)
# 	# 	products =  frappe.db.sql(ord_query, as_dict=True)
# 	# 	res_data = get_product_details(products)
# 	# 	if res_data:
# 	# 		recommended_products.append(res_data[0])

# 		# s = """select p.item, p.tax_category, p.price, p.old_price, p.short_description, p.full_description, p.sku, p.name ,p.route,
# 		# p.inventory_method, p.minimum_order_qty, p.maximum_order_qty, p.stock, p.disable_add_to_cart_button,
# 		# (select list_image from `tabProduct Image` where parent=p.name order by is_primary desc limit 1) as product_image,
# 		# (select brand_name from `tabProduct Brand Mapping` where parent=p.name  limit 1) as product_brand,
# 		# (select B.route from `tabProduct Brand Mapping` MP inner join `tabProduct Brand` B on MP.brand=B.name where MP.parent=p.name and
# 		# B.published=1 limit 1) as brand_route
# 		#   from `tabProduct` p where p.is_active =1 and p.display_home_page = 1 """
# 	if catalog_settings.enable_recetly_viewed_products and customer:
# 		recently_viewed_products = get_customer_recently_viewed_products(customer, domain, isMobile,business)
# 	you_may_like = get_bought_together(business=business, isMobile=isMobile)
# 	return {
# 		'best_seller_category': best_sellers,
# 		'related_products': related_products,
# 		'cross_selling_products':cross_selling_products,
# 		'products_purchased_together': customer_bought,
# 		'recommended_products':recommended_products,
# 		'product_category': (categories_list[0] if categories_list else {}),
# 		'recently_viewed_products': recently_viewed_products,
# 		'you_may_like':you_may_like,
# 		'related_categories':related_categories
# 		}


# def get_parent_categorie(category):
# 	try:
# 		count = frappe.db.get_value('Product Category', category, ['lft', 'rgt'], as_dict=True)
# 		if count:
# 			query = 'select name from `tabProduct Category` where is_active = 1 and disable_in_website = 0 and lft <= {lft} and rgt >= {rgt}'.format(lft=count.lft, rgt=count.rgt)
# 			return frappe.db.sql('''{query}'''.format(query=query), as_dict=1)
# 		else:
# 			return []
# 		# return frappe.db.get_all('Product Category', fields=['name'], filters={'is_active': 1, 'parent_product_category': category}, limit_page_length=100)
# 	except Exception:
# 		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store.ecommerce_business_store.api.get_parent_categorie')

@frappe.whitelist(allow_guest=True)
def get_uploaded_file_content(filedata):
    try:

        import base64
        if filedata:
            if "," in filedata:
                filedata = filedata.rsplit(",", 1)[1]
            uploaded_content = base64.b64decode(filedata)
            return uploaded_content
        else:
            frappe.msgprint(_('No file attached'))
            return None

    except Exception as e:
        frappe.log_error(frappe.get_traceback(
        ), "ecommerce_business_store.ecommerce_business_store.mobileapi.get_uploaded_file_content")


@frappe.whitelist()
def get_side_menu_fields(dt):
    linked_docs = frappe.db.sql(
        """ SELECT fieldname FROM `tabDocField` WHERE parent=%(dt)s AND fieldtype='Data' """, {"dt": dt}, as_dict=1)
    return linked_docs


@frappe.whitelist()
def get_linked_docs(doctype, txt, searchfield, start, page_len, filters):
    dt = filters.get("document")
    linked_docs = frappe.db.sql(
        """ SELECT options,fieldname FROM `tabDocField` WHERE parent=%(dt)s AND fieldtype='Link' """, {"dt": dt})
    return linked_docs


@frappe.whitelist()
def get_linked_fields(document):
    linked_docs = frappe.db.sql(""" SELECT options,fieldname FROM `tabDocField` WHERE parent=%(dt)s AND fieldtype='Link' """, {
        "dt": document}, as_dict=1)
    return linked_docs


@frappe.whitelist(allow_guest=True)
def update_doc(doc):
    try:
        from six import string_types
        if isinstance(doc, string_types):
            doc = json.loads(doc)
        keys = doc.keys()
        if frappe.db.exists(doc.get('doctype'), doc.get('name')):
            update_doc = frappe.get_doc(doc.get('doctype'), doc.get('name'))
            for key in keys:
                if type(doc.get(key)) != list:
                    setattr(update_doc, key, doc.get(key))
                # elif type(doc.get(key)) == list:
                # 	setattr(update_doc, key, [])
                # 	for item in doc.get(key):
                # 		update_doc.append(key, item)
            # update_doc.modified = get_today_date(replace=True)
            # if frappe.session.user != 'Guest':
            # 	update_doc.modified_by = frappe.session.user
            update_doc.save(ignore_permissions=True)
            return update_doc.as_dict()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(
        ), "ecommerce_business_store.ecommerce_business_store.mobileapi.update_doc")


@frappe.whitelist()
def get_global_fonts(parent):
    try:
        query_1 = ''' SELECT title,font_weight,font_family FROM `tabGlobal Fonts` WHERE parent="%s" ''' % parent
        return frappe.db.sql(query_1, as_dict=1)
    except Exception:
        frappe.log_error(frappe.get_traceback(
        ), "go1_cms.go1_cms.doctype.web_page_builder.web_page_builder.get_global_fonts")
