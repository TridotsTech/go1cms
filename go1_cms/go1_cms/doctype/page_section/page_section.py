# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import os
import urllib.parse
from frappe.utils import encode, get_files_path , getdate, to_timedelta,  flt
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils.password import encrypt
from go1_cms.go1_cms.api import get_business_from_login, check_domain, get_today_date
from go1_cms.go1_cms.api import get_template_folder, unescape
from urllib.parse import urljoin, unquote, urlencode

class PageSection(Document):
	 
	def validate(self):
		# getting field information of the selected doctype
		if self.section_type == 'Custom Section' and self.content_type == 'Dynamic':
			fields = []
			if self.fetch_product:
				fields = ["name", "price", "old_price", "short_description", "full_description", "sku", "route", "enable_preorder_product","weight","gross_weight",
					"inventory_method", "minimum_order_qty", "maximum_order_qty", "stock", "disable_add_to_cart_button",
					"image", "thumbnail", "product_brand", "item", "custom_entered_price"]
			else:
				if self.reference_document == 'Product Brand':
					fields = ["brand_name", "route", "brand_logo"]
				elif self.reference_document == 'Product Category':
					fields = ["category_name", "category_image", "menu_image", "mobile_image", "route"]
				elif self.reference_document == 'Subscription Plan':
					fields = ["name", "price"]
			self.field_list = json.dumps(fields)
		elif self.section_type in ['Slider', 'Slider With Banner']:
			fields = ["web_image", "mobile_app_image", "mobile_image", "title", "sub_title", "button_text", "redirect_url"]
			self.field_list = json.dumps(fields)

		if not self.section_type == 'Predefined Section':
			self.is_login_required = 0
		self.context = "data"+self.name.lower().replace('-','')
		self.generate_route()
		enable_generate_html=frappe.db.get_single_value("CMS Settings", "generate_html")
		if enable_generate_html:
			generate_section_html(self.name)
		self.check_content_fields()

	def check_content_fields(self):
		if self.content:
			for item in self.content:
				if item.field_label and not item.field_key:
					item.field_key = item.field_label.lower().replace(' ', '_')
					check_existing = list(filter(lambda x: (x.field_key == item.field_key and x.name != item.name), self.content))
					if check_existing:
						item.field_key = item.field_key + '_{0}'.format(len(check_existing))

	def generate_route(self):
		if self.section_type not in ['Slider', 'Slider With Banner']:
			if not self.route:
				encrypted = encrypt(self.name)
				url = 'offers-list'
				if self.reference_document and (self.reference_document == 'Product' or self.fetch_product == 1):
					url = 'products-list'
				self.route = '/{0}?token={1}'.format(url, encrypted)

			if self.content:
				for item in self.content:
					if item.get('field_key') == 'view_all_route' and not item.content:
						item.content = self.route

	def on_update(self):
		#created by boopathy
		if not self.class_name:
			
			self.class_name = get_class_name()
			self.save()

		#end

		pages = frappe.db.sql('''select distinct parent from `tabMobile Page Section` where section = %(section)s and parenttype="Web Page Builder"''',{'section': self.name}, as_dict=1)
		if pages:
			for item in pages:
				doc = frappe.get_doc('Web Page Builder', item.parent)
				doc.run_method('validate')

	
	def section_data(self, customer=None, add_info=None,store_business=None):
		json_obj = {}
		json_obj['section'] = self.name
		json_obj['class_name'] = self.class_name
		json_obj['section_name'] = self.section_title
		json_obj['section_type'] = self.section_type
		json_obj['content_type'] = self.content_type
		json_obj['reference_document'] = self.reference_document
		json_obj['no_of_records'] = self.no_of_records
		json_obj['view_type'] = self.view_type
		json_obj['view_more_redirect_to'] = self.view_more_redirect_to
		json_obj['mobile_app_template'] = self.mobile_app_template
		json_obj['login_required'] = self.is_login_required
		json_obj['dynamic_data'] = self.dynamic_data
		json_obj['is_full_width'] = self.is_full_width
		json_obj['layout_json'] = self.layout_json
		if self.section_type == 'Predefined Section' and not self.is_login_required:
			if self.predefined_section=="Recommended Items":
				# frappe.log_error("rec", "recommended")
				json_obj['data'] = get_recommended_products(self.query, self.reference_document, self.no_of_records, business=self.business, customer=customer, add_info=add_info,store_business=store_business)
				json_obj['reference_document'] = self.reference_document
			else:
				json_obj['data'] = get_data_source(self.query, self.reference_document, self.no_of_records, business=self.business, customer=customer, add_info=add_info,store_business=store_business)
				json_obj['reference_document'] = self.reference_document
		elif self.section_type in ['Slider', 'Slider With Banner']:
			slider_cond = ''
			if self.business:
				slider_cond = ' and business = "{0}"'.format(self.business)
			if check_domain("multi_store") and not store_business:
				multi_store_business = frappe.request.cookies.get('selected_store')
				if not multi_store_business:
					all_locations = frappe.db.get_all("Business",fields=['name','restaurant_name'],order_by="is_default desc")
					if all_locations:
						multi_store_business = all_locations[0].name
				else:
					multi_store_business = unquote(frappe.request.cookies.get('selected_store'))
				if multi_store_business:		
					slider_cond = ' and business = "{0}"'.format(multi_store_business)
			if check_domain("multi_store"):
				if store_business:
					slider_cond = ' and business = "{0}"'.format(store_business)
			json_obj['data'] = frappe.db.sql('''select business,mobile_app_image,mobile_app_videoyoutube_id,mobile_image,mobile_videoyoutube_id,redirect_url,slider_type,upload_video_for_mobile,upload_video_for_mobile_app,upload_video_for_web,video_type,web_image,web_videoyoutube_id from `tabSlider` where published = 1 {cond} order by display_order'''.format(cond=slider_cond), as_dict=1)
		elif self.section_type == 'Custom Section':
			if self.content_type == 'Static':
				if self.reference_document == 'Product Category':
					json_obj['route'] = frappe.db.get_value(self.reference_document, self.reference_name, "route")
				json_obj['data'] = json.loads(self.custom_section_data)
			else:
				if self.reference_document == 'Product Category' and self.dynamic_data==0:
					json_obj['data'] = json.loads(self.custom_section_data)
				else:
					json_obj['reference_document'] = self.reference_document
					json_obj['reference_name'] = self.reference_name
					json_obj['data'] = get_dynamic_data_source(self, customer=customer,store_business=store_business)
					json_obj['fetch_product'] = self.fetch_product
					if len(json_obj['data']) > 0 and self.reference_name:
						field = None
						if self.reference_document == 'Product Category':
							field = 'category_name'
						if self.reference_document == 'Product Brand':
							field = 'brand_name'
						if self.reference_document == 'Subscription Plan':
							field = 'name'
						if self.reference_document == 'Author':
							field = 'name'
						if self.reference_document == 'Publisher':
							field = 'name'
						if field:
							json_obj['title'] = frappe.db.get_value(self.reference_document, self.reference_name, field)
							if self.reference_document == 'Product Category':
								json_obj['route'] = frappe.db.get_value(self.reference_document, self.reference_name, "route")
		
		elif self.section_type == 'Tabs' and self.reference_document == 'Custom Query':
			if self.reference_document == 'Custom Query':
				data = json.loads(self.custom_section_data)
				for item in data:
					no_of_records = 10
					if item.get('no_of_records'):
						no_of_records = item.get('no_of_records')
					item['name'] = item.get('tab_item').lower().replace(' ', '_')
					query_item = frappe.db.get_value(self.reference_document, item.get('tab_item'), 'query')
					query='''{query} limit {limit}'''.format(query=query_item,limit=no_of_records)
					result = frappe.db.sql(query, {"business":self.business}, as_dict=1)
					result = get_product_details(result, customer=customer)
					item['products'] = result
					org_datas = []
					org_datas = get_products_json(result)
					item['products'] = org_datas
				json_obj['data'] = data

	
		if self.content:
			for item in self.content:
				if item.field_type != 'List':
					json_obj[item.field_key] = item.content
				else:
					json_obj[item.field_key] = json.loads(item.content) if item.content else []

		return json_obj

	def validate_sql_condition(self):
		if self.condition == '':
			return False
		if self.condition.find(';') > -1:
			return False
		if self.condition.find('update') > -1:
			return False
		if self.condition.find('delete') > -1:
			return False

		return True
def get_products_json(data):
	org_datas = []
	for product in data:
		product_attributes = []
		for x in product.get("product_attributes"):
			options = []
			for option in x.get("options"):
				options.append({
					"attr_itemprice": option.get("attr_itemprice"),
       				"attr_oldprice":option.get("attr_oldprice"),
       				"is_pre_selected": option.get("is_pre_selected"),
			        "name": option.get("name"),
			        "option_value": option.get("option_value"),
			        "price_adjustment": option.get("price_adjustment"),
			        "product_title": option.get("product_title"),
					})
			product_attributes.append({
				"attribute":x.get("attribute"),
				"attribute_unique_name":x.get("attribute_unique_name"),
				"control_type":x.get("control_type"),
				"is_required":x.get("is_required"),
				"name":x.get("name"),
				"options":options
				})
		org_datas.append({
			"image": product.get("image"),
			"image_type":product.get("image_type"),
		    "actual_old_price":product.get("actual_old_price"),
		    "actual_price": product.get("actual_price"),
		    "attribute_old_price": product.get("attribute_old_price"),
		    "attribute_price":product.get("attribute_price"),
		    "brand_route": product.get("brand_route"),
		    "disable_add_to_cart_button": product.get("disable_add_to_cart_button"),
		    "discount_percentage": product.get("discount_percentage"),
		    "enable_preorder_product": product.get("enable_preorder_product"),
		    "has_attr_stock": product.get("has_attr_stock"),
		    "have_attribute": product.get("have_attribute"),
		    "inventory_method":product.get("inventory_method"),
		    "item": product.get("item"),
		    "item_title": product.get("item_title"),
		    "maximum_order_qty": product.get("maximum_order_qty"),
		    "minimum_order_qty": product.get("minimum_order_qty"),
		    "name": product.get("name"),
		    "old_price": product.get("old_price"),
		    "price":product.get("price"),
		    "product_attributes":product_attributes,
		    "product_brand": product.get("product_brand"),
		    "product_image": product.get("product_image"),
		    "rating":product.get("rating"),
		    "review_count": product.get("review_count"),
		    "route": product.get("route"),
		    "short_description":product.get("short_description"),
		    "sku": product.get("sku"),
		    "stock": product.get("stock"),
		    "thumbnail": product.get("thumbnail"),
		    "weight": product.get("weight"),
		    "gross_weight": product.get("gross_weight"),
		    "show_attributes_inlist":product.get("show_attributes_inlist"),
		    "variant_price": product.get("variant_price")

		})
	return org_datas

def get_data_source(query, dt=None, no_of_records=0, login_required=0, customer=None, user=None, business=None, 
	latitude=None, longitude=None, order_type=None, page_no=0, add_info=None,store_business=None):
	if no_of_records > 0:
		start = int(page_no) * int(no_of_records)
		query = '{0} limit {1},{2}'.format(query, start, no_of_records)
	if not business:
		business = get_business_from_login()
	if check_domain("multi_store") and not store_business:
		multi_store_business = frappe.request.cookies.get('selected_store')
		if not multi_store_business:
			all_locations = frappe.db.get_all("Business",fields=['name','restaurant_name'],order_by="is_default desc")
			if all_locations:
				multi_store_business = all_locations[0].name
		else:
			multi_store_business = unquote(frappe.request.cookies.get('selected_store'))
		if multi_store_business:		
			query = query.replace('where p.is_active','where  p.restaurant = "{0}" AND p.is_active '.format(multi_store_business))
			query  = query.replace('where parent_product_category is null and','where  parent_product_category is null and business = "{0}" AND '.format(multi_store_business))
	if check_domain("multi_store"):
		if store_business:
			query = query.replace('where p.is_active','where  p.restaurant = "{0}" AND p.is_active '.format(store_business))
			query  = query.replace('where parent_product_category is null and','where  parent_product_category is null and business = "{0}" AND '.format(store_business))
	if check_domain('saas'):
		domain = frappe.get_request_header('host')
		business = get_business_from_web_domain(domain)
		if business:
			query = query.replace('where p.is_active','where  p.restaurant = "{0}" AND p.is_active '.format(business))

	# if check_domain("multi_store"):
	# 	if frappe.request.cookies.get('selected_store'):
	# 		query = query.replace('where p.is_active','where  p.restaurant = "{0}" AND p.is_active '.format(unquote(frappe.request.cookies.get('selected_store'))))
	filters = {}
	filters['business'] = business
	filters['restaurant'] = business
	if latitude:
		filters['latitude'] = latitude
	if longitude:
		filters['longitude'] = longitude
	if login_required:
		if not customer:
			customer = urllib.parse.unquote(frappe.request.cookies.get('customer_id')) if frappe.request.cookies.get('customer_id') else None
		if not user:
			user = frappe.session.user
		filters['customer'] = customer
		filters['user'] = user
	if add_info:
		for k, v in add_info.items():
			filters[k] = urllib.parse.unquote(v)
			if k == 'searchText' or k == 'searchTxt':
				filters[k] = urllib.parse.unquote(v) + '%'
	if check_domain('restaurant'):
		today = get_today_date(replace=True)
		filters['today_date'] = getdate(today)
		filters['today_time'] = str(today.time())
		if order_type:
			filters['order_type'] = order_type
		filters['distance'] = get_settings_value_from_domain('Business Setting', 'nearby_distance', business=business)
		unit = get_settings_value_from_domain('Business Setting', 'distance_unit', business=business)
		if unit != 'Miles':
			filters['distance'] = float(filters['distance']) * 0.621371
		try:
			if not latitude and not longitude:
				check_cookie = frappe.request.cookies.get('geoLocation')
				if check_cookie:
					vals = urllib.parse.unquote(check_cookie)
					filters['latitude'], filters['longitude'] = vals.split(',')
			if not order_type:
				filters['order_type'] = frappe.request.cookies.get('order_type')
			order_date = frappe.request.cookies.get('order_date')
			if order_date: filters['today_date'] = getdate(urllib.parse.unquote(order_date))
			order_time = frappe.request.cookies.get('order_time')
			if order_time:
				time = urllib.parse.unquote(order_time)
				if time != 'ASAP':
					time = to_timedelta(time)
				else:
					time = str(today.time())
				filters['today_time'] = time
		except Exception as e:
			print(e)
			pass
	try:
		result = frappe.db.sql('''{query}'''.format(query=query), filters, as_dict=1)
		if result and dt == 'Product':
			result = get_product_details(result)
		
		return result
	except Exception as e:
		frappe.log_error(frappe.get_traceback(),"ecommerce_business_store.cms.doctype.page_section.page_section.get_data_source")
		return []

def get_recommended_products(query=None, dt=None, no_of_records=0, login_required=0, customer=None, user=None, business=None, 
	latitude=None, longitude=None, order_type=None, page_no=0, add_info=None,store_business=None):
	catalog_settings = get_settings_from_domain('Catalog Settings')
	recommended_products = []
	recommended_item_list = ""
	if catalog_settings.enable_recommended_products:
		viewed_items = []
		# frappe.log_error(customer, "---customer--rec-")
		if customer:
			cond = " where o.customer='{customer}'""".format(customer=customer)
			viewed_query = """select distinct product from `tabCustomer Viewed Product` where parent ='{customer}'""".format(customer=customer)
			viewed_items = frappe.db.sql(viewed_query, as_dict=True)
			# frappe.log_error(viewed_items, "viewed_items")
		
			orderquery = """select MAX(i.item) as product from `tabOrder` o inner join `tabOrder Item` i ON i.parent=o.name  {cond}""".format(cond=cond)
			order_items = frappe.db.sql(orderquery, as_dict=True)
			# frappe.log_error(order_items, "order_items")
			
			cartquery = """select i.product, i.price from `tabShopping Cart` o inner join `tabCart Items` i ON i.parent=o.name  {cond}""".format(cond=cond)
			cart_items = frappe.db.sql(cartquery, as_dict=True)
			# frappe.log_error(cart_items, "cart_items")
			for n in cart_items:
				order_items.append(n)
			for s in viewed_items:
				order_items.append(s)
			for s in order_items:
				s.price = frappe.db.get_value("Product", s.product, "price")
			if not order_items:
				order_items = []
			
		else:
			cond = ""
		
			orderquery = """select MAX(i.item) as product from `tabOrder` o inner join `tabOrder Item` i ON i.parent=o.name  {cond}""".format(cond=cond)
			order_items = frappe.db.sql(orderquery, as_dict=True)
			# frappe.log_error(order_items, "order_items")
			for s in order_items:
				s.price = frappe.db.get_value("Product", s.product, "price")
			if not order_items:
				order_items = []
		# frappe.log_error(order_items, "order_items")
		recommended_item_list=",".join(['"' + x.product + '"' for x in order_items if x.product])
		catquery = """select distinct category from `tabProduct Category Mapping`"""
		if recommended_item_list:
			catquery = """select distinct category from `tabProduct Category Mapping` where parent in ({lists})""".format(lists=recommended_item_list)
		# frappe.log_error(catquery, "cat_items")
		cat_items = frappe.db.sql(catquery, as_dict=True)
		max_val = max(flt(node.price) for node in order_items)
		min_val = min(flt(node.price) for node in order_items)
		category_list = []
		category_list=",".join(['"' + x.category + '"' for x in cat_items])
		if category_list:
			ord_query = """select p.*,(select list_image from `tabProduct Image` where parent=p.name order by is_primary desc limit 1) as product_image from `tabProduct` p inner join `tabProduct Category Mapping` pc on pc.parent=p.name where pc.category in ({category_list}) and p.price >='{min_val}' and p.price <='{max_val}' limit 1,{no_of_records}""".format(no_of_records=no_of_records,lists=recommended_item_list, category_list=category_list,min_val=min_val, max_val=max_val)
		else:
			ord_query = """select p.*,(select list_image from `tabProduct Image` where parent=p.name order by is_primary desc limit 1) as product_image from `tabProduct` p inner join `tabProduct Category Mapping` pc on pc.parent=p.name where  p.price >='{min_val}' and p.price <='{max_val}' limit 1,{no_of_records}""".format(no_of_records=no_of_records,lists=recommended_item_list, category_list=category_list,min_val=min_val, max_val=max_val)
		products =  frappe.db.sql(ord_query, as_dict=True)	
		# frappe.log_error(products, "products")
		res_data = get_product_details(products)
		# frappe.log_error(res_data, "res_data")
		if res_data:
			recommended_products = res_data
	return recommended_products


def get_dynamic_data_source(doc, customer=None,store_business=None):
	result = []
	condition = ""
	business = None
	if not business:
		business = get_business_from_login()
	if doc.condition: condition = ' and {0}'.format(doc.condition)
	if doc.fetch_product: 
		if doc.reference_document == 'Product Category':
			child_doc = 'Product Category Mapping'
		elif doc.reference_document == 'Author':
			child_doc = 'Author'
		elif doc.reference_document == 'Publisher':
			child_doc = 'Publisher'
		else:
			child_doc = 'Product Brand Mapping'
		cat_field = ' doc.is_active,'
		if doc.reference_document == 'Product Category':
			#hided by boopathy
			# from ecommerce_business_store.ecommerce_business_store.api import get_child_categories
			#end
			cat_field += ' child.category,'
			child = get_child_categories(doc.reference_name)
			child_category = '""'
			if child:
				child_category = ",".join(['"' + x.name + '"' for x in child])
			condition += ' and (child.category = "{0}" or child.category in ({1}))'.format(doc.reference_name, child_category)

		elif doc.reference_document == 'Product Brand':
			condition += ' and child.brand = "%s"' % doc.reference_name	
		elif doc.reference_document == 'Author':
			condition += ' and doc.author = "%s"' % doc.reference_name
		elif doc.reference_document == 'Publisher':
			condition += ' and doc.publisher = "%s"' % doc.reference_name
		if business:
			condition += ' and doc.restaurant = "{0}"'.format(business)
		if check_domain("multi_store"):
			multi_store_business = frappe.request.cookies.get('selected_store')
			if not store_business:
				if not multi_store_business:
					all_locations = frappe.db.get_all("Business",fields=['name','restaurant_name'],order_by="is_default desc")
					if all_locations:
						multi_store_business = all_locations[0].name
				else:
					multi_store_business = unquote(frappe.request.cookies.get('selected_store'))
				if multi_store_business:		
					condition += "AND doc.restaurant = '{0}' ".format(multi_store_business)
		if check_domain("multi_store"):
			if store_business:		
				condition += "AND doc.restaurant = '{0}' ".format(store_business)
		if check_domain('saas'):
			domain = frappe.get_request_header('host')
			business = get_business_from_web_domain(domain)
			if business:
				condition += "AND doc.restaurant = '{0}' ".format(business)
		# if check_domain("multi_store"):
		# 	condition += " AND doc.restaurant = '{0}' ".format(unquote(frappe.request.cookies.get('selected_store')))
		books_columns_query = ''
		books_join_query = ''
		installed_apps = frappe.db.sql(''' select * from `tabModule Def` where app_name='book_shop' ''', as_dict=True)
		if len(installed_apps) > 0:
			books_columns_query = ',AU.author_name,AU.route as author_route,PU.publisher_name,PU.route as publisher_route'
			books_join_query = '  left join `tabAuthor` AU on AU.name=doc.author left join `tabPublisher` PU on PU.name=doc.publisher'

		query = '''SELECT doc.name, doc.item,doc.item as item_title, doc.tax_category, doc.price, doc.old_price, doc.short_description,doc.enable_preorder_product, doc.weight,doc.gross_weight, 
			doc.full_description, doc.sku, doc.route, doc.inventory_method, doc.minimum_order_qty {books_columns_query}, 
			doc.maximum_order_qty, doc.stock, doc.disable_add_to_cart_button,doc.custom_entered_price, (select list_image from `tabProduct Image` i where parent = doc.name order by is_primary desc limit 1) as image,{cat_field} 
			(select detail_thumbnail from `tabProduct Image` i where parent = doc.name order by is_primary desc limit 1) as thumbnail,
			(select list_image from `tabProduct Image` i where parent = doc.name order by is_primary desc limit 1) as product_image,
			(select brand_name from `tabProduct Brand Mapping` where parent = doc.name limit 1) as product_brand,
			(select B.route from `tabProduct Brand Mapping` MP inner join `tabProduct Brand` B on MP.brand = B.name
			where MP.parent = doc.name and B.published = 1 limit 1) as brand_route from `tabProduct` doc {books_join_query} left join 
			`tab{doctype}` child on child.parent = doc.name where doc.is_active = 1 {condition} group by doc.name order by 
			doc.{field} {sort_by} limit {limit}'''.format(books_join_query=books_join_query,books_columns_query = books_columns_query,condition=condition, doctype=child_doc, cat_field=cat_field, field=(doc.sort_field or 'name'), sort_by=doc.sort_by, limit=doc.no_of_records)
		if doc.display_randomly:
			query = '''SELECT doc.name, doc.item,doc.item as item_title, doc.tax_category, doc.price, doc.old_price, doc.short_description,doc.enable_preorder_product, doc.weight,doc.gross_weight, 
			doc.full_description, doc.sku, doc.route, doc.inventory_method, doc.minimum_order_qty {books_columns_query}, 
			doc.maximum_order_qty, doc.stock, doc.disable_add_to_cart_button,doc.custom_entered_price, (select list_image from `tabProduct Image` i where parent = doc.name order by is_primary desc limit 1) as image,{cat_field} 
			(select detail_thumbnail from `tabProduct Image` i where parent = doc.name order by is_primary desc limit 1) as thumbnail,
			(select list_image from `tabProduct Image` i where parent = doc.name order by is_primary desc limit 1) as product_image,
			(select brand_name from `tabProduct Brand Mapping` where parent = doc.name limit 1) as product_brand,
			(select B.route from `tabProduct Brand Mapping` MP inner join `tabProduct Brand` B on MP.brand = B.name
			where MP.parent = doc.name and B.published = 1 limit 1) as brand_route from `tabProduct` doc {books_join_query} left join 
			`tab{doctype}` child on child.parent = doc.name where doc.is_active = 1 {condition} group by doc.name order by 
			RAND() limit {limit}'''.format(books_join_query=books_join_query,books_columns_query = books_columns_query,condition=condition, doctype=child_doc, cat_field=cat_field,  sort_by=doc.sort_by, limit=doc.no_of_records)
		
		# frappe.log_error(query,"ecommerce_business_store.cms.doctype.page_section.page_section.get_data_source")
		result = frappe.db.sql(query, as_dict=1)
		result = get_product_details(result, customer=customer)
		org_datas = []
		org_datas = get_products_json(result)
		return org_datas
	else:
		fields = '*'
		if doc.reference_document == 'Product Category':
			fields = 'category_name, category_image, menu_image,route'
			condition = ' where is_active = 1 {0}'.format(condition)
		elif doc.reference_document == 'Product Brand':
			fields = 'brand_name, route, brand_logo'
			condition = ' where published = 1 {0}'.format(condition)
		elif doc.reference_document == 'Subscription Plan':
			fields = 'name, price'
			condition += ' where disabled = 0'
		if business:
			condition += ' and business = "{0}"'.format(business)
		if doc.reference_document not in ["Product Category", "Product Brand", "Subscription Plan"]:
			condition = ' where name != "" {0}'.format(condition)
		if check_domain("multi_store") and doc.reference_document == 'Product Category':
			multi_store_business = frappe.request.cookies.get('selected_store')
			if not multi_store_business:
				all_locations = frappe.db.get_all("Business",fields=['name','restaurant_name'],order_by="is_default desc")
				if all_locations:
					multi_store_business = all_locations[0].name
			else:
				multi_store_business = unquote(frappe.request.cookies.get('selected_store'))
			if multi_store_business:		
				condition += "AND doc.business = '{0}' ".format(multi_store_business)
		if check_domain('saas'):
			domain = frappe.get_request_header('host')
			business = get_business_from_web_domain(domain)
			if business:
				condition += "AND doc.business = '{0}' ".format(business)
		query = '''SELECT {fields} from `tab{doctype}` doc {condition} order by doc.{field} {sort_by} limit {limit}'''.format(fields=fields, doctype=doc.reference_document, condition=condition, field=(doc.sort_field or 'name'), sort_by=doc.sort_by, limit=doc.no_of_records)
		result = frappe.db.sql(query, as_dict=1)
	return result

@frappe.whitelist()
def get_item_info(dt, dn):
	doc = frappe.get_doc(dt, dn)
	meta = frappe.get_meta(dt)
	title_value = ''
	if meta.title_field:
		title_value = doc.get(meta.title_field)
	else:
		title_value = doc.name
	images = []
	if dt == 'Product':
		images = frappe.db.sql('''select list_image, detail_thumbnail as thumbnail from `tabProduct Image` where parent = %(parent)s order by idx''',{'parent': dn}, as_dict=1)
	else:
		fields = filter(lambda x: x.fieldtype in ['Attach', 'Attach Image'], meta.fields)
		for item in fields:
			if doc.get(item.fieldname):
				images.append({'thumbnail': doc.get(item.fieldname)})
	return {'title': title_value, 'images': images}

@frappe.whitelist()
def update_page_sections():
	doc_list = frappe.db.sql('''select name from `tabPage Section` where section_type <> "Banner" or (section_type = "Custom Section" and content_type = "Dynamic")''', as_dict=1)
	if doc_list:
		for item in doc_list:
			doc = frappe.get_doc('Page Section', item.name)
			doc.save(ignore_permissions=True)

@frappe.whitelist()
def save_as_template(section, title):
	doc = get_mapped_doc("Page Section", section, {
		"Page Section": {
			"doctype": "Section Template"
		},
		"Section Content":{
			"doctype": "Section Content"
		}
	}, None, ignore_permissions=True)
	doc.name = title
	doc.save(ignore_permissions=True)
	return doc

@frappe.whitelist()
def get_section_template(section):
	return frappe.get_doc('Section Template', section)

def get_section_data(section, customer=None):
	section_data = frappe.db.sql('''select section, parent, parentfield from `tabMobile Page Section` where section = %(name)s''', {'name': section}, as_dict=1)
	data_source = None
	if section_data:
		path = 'data_source/{0}_{1}.json'.format(section_data[0].parent.lower().replace(' ', '_'), ('web' if section_data[0].parentfield == 'web_section' else 'mobile'))
		origin = get_files_path()
		file_path = os.path.join(origin, path)
		if os.path.exists(file_path):
			with open(file_path) as f:
				data = json.loads(f.read())
				data_source = next((x for x in data if x.get('section') == section), None)
				if data_source['login_required'] == 1 and (frappe.session.user != 'Guest' or customer):
					doc = frappe.get_doc('Page Section', section)
					data_source['data'] = get_data_source(doc.query, doc.reference_document, doc.no_of_records, 1, customer)
				if data_source['dynamic_data'] == 1:
					if data_source['section_type'] in ['Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
						doc = frappe.get_doc('Page Section', data_source['section'])
						data_source = doc.run_method('section_data')
	return data_source

#by siva
def generate_section_html(section, view_type=None, content_type="Dynamic"):
	if content_type=="Static":
		generate_static_section(section)

	if content_type=="Dynamic":
		generate_dynamic_section(section, view_type)

def generate_static_section(section):
	context={}
	template = ""
	business=None
	product_template = frappe.db.get_value("Page Section", section, ["name", "business", "section_title", "web_template", "custom_css", "custom_js"], as_dict=True)	
	if product_template:
		if product_template.business:
			business=product_template.business
		data_source = get_section_data(section)
		template = product_template.web_template
		if product_template.custom_css:
			template += '\n <style> \n'  + product_template.custom_css + '\n </style>\n'
		if product_template.custom_js:
			template += '\n{% block script %}\n <script> \n'  + product_template.custom_js + '\n </script>\n{% endblock %}\n'
		template=frappe.render_template(template, {
			'data_source': data_source,
			'currency': frappe.cache().hget('currency', 'symbol')
			})
		temp_path = get_template_folder(business=business)
		html_page = product_template.section_title.lower().replace(' ','-') + "-" + (product_template.name).lower().replace(' ','-')
		with open(os.path.join(temp_path, (html_page+'.html')), "w") as f:
			temp = unescape(encode(template))
			f.write(temp)

def generate_dynamic_section(section, view_type):	
	template = ""
	business=None
	# hide by gopi on 20/10/22
	# product_template = frappe.db.get_value("Page Section", section, ["name", "business","section_title", "web_template", "mobile_view_template", "custom_css", "custom_js"], as_dict=True)	
	product_template = frappe.db.get_value("Page Section", section, ["name","section_title", "web_template", "mobile_view_template", "custom_css", "custom_js"], as_dict=True)	
	# end
	if product_template:
		#context={}
		#content = frappe.db.get_all("Section Content", fields=["*"], filters={"parent":product_template.name})
		#for con in content:
		#	context[con.field_key]=con.content
		if product_template.business:
			business=product_template.business
		if product_template.web_template:
			template += product_template.web_template
		if product_template.mobile_view_template:
			template +=product_template.mobile_view_template
		if not template:
			template = ''
		if product_template.custom_css:
			template += '\n <style> \n'  + str(product_template.custom_css or '') + '\n </style>\n'
		if product_template.custom_js:
			template += '\n <script> \n'  + str(product_template.custom_js or '') + '\n </script>\n'
		temp_path = get_template_folder(business=business)
		html_page = product_template.section_title.lower().replace(' ','-') + "-" + (product_template.name).lower().replace(' ','-')
		with open(os.path.join(temp_path, (html_page+'.html')), "w") as f:
			#temp = unescape(encode(template))
			temp = template
			f.write(temp)
		
def get_class_name():
		import string
		import random
		res = ''.join(random.choices(string.ascii_lowercase, k = 8))
		if frappe.db.get_all("Page Section",filters={"class_name":res}):
			return get_class_name()
		else:
			return res




#added by boopathy from ecommerce business store api on 10/08/2022
def get_product_details(product, isMobile=0, customer=None, current_category=None):
	media_settings = get_settings_from_domain('Media Settings')
	catalog_settings = get_settings_from_domain('Catalog Settings')
	if product:
		today_date = get_today_date(replace=True)
		discount_list = frappe.db.sql(""" SELECT name FROM `tabDiscounts` WHERE 
									  (discount_type = 'Assigned to Products' OR discount_type = 'Assigned to Categories' OR discount_type = 'Assigned to Business')
									  AND 
									  (CASE 
									  	WHEN start_date is not null then start_date <= "{today}"
		    							ELSE 1 = 1 end) 
		    						  AND (
		    						  CASE 
		    						  	WHEN end_date is not null then end_date >= "{today}"
		    						  	ELSE 1 = 1 end)
		    						  """.format(today=today_date),as_dict=1)
		for x in product:
			x.actual_price = x.price
			x.actual_old_price = x.old_price
			x.item_title = x.item
			x.role_based_price = 0
			# code inserted by shankar on 21-04-2020 for Product Price rule
			if check_domain('b2b'):
				role = frappe.get_roles(frappe.session.user)
				roles = ','.join('"{0}"'.format(r) for r in role)
				query = '''SELECT price FROM `tabProduct Pricing Rule` WHERE parent="{product}" AND parentfield="pricing_rule" AND role IN ({roles}) ORDER BY creation DESC'''.format(roles=roles,product=x.name)
				product_pricing_rule = frappe.db.sql('''{query}'''.format(query=query),as_dict=1)
				if product_pricing_rule:
					x.price = product_pricing_rule[0].price
					x.role_based_price = 1
			#end of code insertion by shankar
			price_details = None
			if discount_list:
				price_details = get_product_price(x, customer=customer)
			product_price = x.price
			if price_details:
				if price_details.get('discount_amount'):
					product_price = price_details.get('rate')
				x.discount_rule = price_details.get('discount_rule')
				x.discount_label = price_details.get('discount_label')
			
			if x.price != product_price:
				x.old_price = x.price
				x.price = product_price
			if check_domain('b2b'):
				if x.role_based_price == 1:
					x.old_price = x.actual_price
			if float(x.old_price) > 0 and float(x.price) < float(x.old_price):
				x.discount_percentage = int(round((x.old_price - x.price) / x.old_price * 100, 0))
			# updated by kartheek for price in lakhs on 9 dec 2019

			if isMobile == 0:
				if float(x.price) > 100000:
					short_amt = float(x.price) / 100000
					x.price = str('%.2f' % short_amt) + 'L'
				else:
					x.price = str('%.2f' % x.price)
				if x.old_price > 0:
					if x.old_price > 100000:
						short_amt = float(x.old_price) / 100000
						x.old_price = str('%.2f' % short_amt) + 'L'
					else:
						x.old_price = str('%.2f' % x.old_price)
				else:
					x.old_price = str('%.2f' % x.old_price)
			# updated by kartheek for price in lakhs on 9 dec 2019
			# if x.image and not x.product_image:
			# 	x.product_image = x.image
			if not x.product_image:
				# for thumbnails by Rajeshwari on 13-12-19
				if media_settings.list_thumbnail:
					x.product_image = media_settings.list_thumbnail
			show_attributes = 0
			mapped_category = frappe.db.get_all('Product Category Mapping', filters={'parent':x.name}, fields=['category'],order_by="idx desc")
			
			x.category_mapping = mapped_category
			if mapped_category:
				product_category=frappe.db.get_all('Product Category',fields=["name","route","category_name"], filters={"name":mapped_category[0].category},order_by="display_order",limit_page_length=1)
				if product_category:
					x.item_categories=product_category[0]
			if mapped_category and len(mapped_category) > 0:
				for category in mapped_category:
					child_categories = get_parent_categorie(category.category)
					if child_categories and len(child_categories) > 0:
						for cat in child_categories:
							item_category = frappe.get_doc('Product Category', cat.name)
							if item_category and item_category.show_attributes_inlist==1:
								if show_attributes==0:
									show_attributes += item_category.show_attributes_inlist
			product_attributes = frappe.db.get_all('Product Attribute Mapping', fields=['*'],
								  filters={'parent': x.name},  order_by='idx', limit_page_length=50)
			check_stock = False
			has_attr_stock = True
			if len(product_attributes) > 0:
				if x.inventory_method == 'Track Inventory By Product Attributes' and len(product_attributes) == 1:
					check_stock = True
					combination = frappe.db.get_all('Product Variant Combination', filters={'parent': x.name}, limit_page_length=500)
					# check_stock = next((x for x in combination if x.stock > 0), None)
					# if check_stock:
					# 	has_attr_stock = True
				attribute_ids = ''
				attribute_ids1 = ''
				attribute = ''
				attribute_price=0
				attribute_old_price = 0
				for attribute in product_attributes:
					attribute.options = frappe.db.get_all('Product Attribute Option',
							fields=['option_value', 'price_adjustment', 'display_order', 'name','image_list','is_pre_selected','attribute_color','product_title'], 
							filters={'parent': x.name, 'attribute': attribute.product_attribute, 'attribute_id': attribute.name},
							order_by='display_order', limit_page_length=500)
					if attribute.options:
						count = 1
						for op in attribute.options:
							# if show_attributes==1:
							if x.inventory_method == 'Track Inventory' or x.inventory_method == 'Dont Track Inventory':
								op.attr_itemprice = float(op.price_adjustment) + float(x.actual_price)
								x.price = op.attr_itemprice
								if op.is_pre_selected==1:
									attribute_ids+=op.name+'\n'
									attribute_price=float(op.attr_itemprice)
									if type(x.old_price) != str:
										attribute_old_price = float(op.price_adjustment) + float(x.old_price)
								else:
									if count == 1:
										attribute_ids+=op.name+'\n'
										attribute_price=float(op.attr_itemprice)
										if type(x.old_price) != str:
											attribute_old_price = float(op.price_adjustment) + float(x.old_price)
								price_detail = get_product_price(x, customer=customer)
								if price_detail and price_detail.get('discount_amount'):
									
									product_price1 = price_detail.get('rate')
									if x.price != product_price1:
										x.old_price = x.actual_price
										x.price = product_price1
										op.attr_itemprice = product_price1
										if op.is_pre_selected==1:
											# attribute_price = 0
											attribute_price=float(product_price1)
											attribute_old_price = float(op.price_adjustment) + float(x.old_price)
										else:
											if count == 1:
												# attribute_price = 0
												attribute_price=float(product_price1)
												attribute_old_price = float(op.price_adjustment) + float(x.old_price)
								count+=1
								if  type(x.old_price) != str and float(x.old_price) > 0:
									op.attr_oldprice = float(op.price_adjustment) + float(x.old_price)
									# attribute_old_price = op.attr_oldprice
							if x.inventory_method == 'Track Inventory By Product Attributes':
								attribute_ids=op.name+'\n'
								variant_comb = validate_attributes_stock(x.name,attribute_ids,attribute,x.minimum_order_qty,add_qty=None)
								if variant_comb:
									op.attr_itemprice = float(variant_comb['price'])
									op.attr_oldprice = float(variant_comb['old_price'])
									if variant_comb.get('discount'):
										if 'rate' in variant_comb['discount']:
											op.attr_itemprice = float(variant_comb['discount']['rate'])
											op.attr_oldprice = float(variant_comb['price'])
									op.status = variant_comb['status']
									# op['stock'] = variant_comb['stock']
									if variant_comb['status'] =="Success":
										if op.stock and int(op.stock) > 0:
											op.has_attr_stock = True
										else:
											op.has_attr_stock = False
									else:
										op.has_attr_stock = False
									if op.is_pre_selected == 1:
										if op.has_attr_stock  == False:
											has_attr_stock = False
							# Inserted by suguna on 05/08/20
							# if op.is_pre_selected==1:
							# 	attribute_ids+=op.name+'\n'
							# 	attribute_price+=float(op.price_adjustment)
							# End
							# op.videos = frappe.get_all('Product Attribute Option Video',filters={"option_id":op.name},fields=["youtube_video_id"])
							op.videos = frappe.get_all('Product Attribute Option Video',filters={"option_id":op.name},fields=["youtube_video_id","video_type"])
							if op.image_list:
								op.images = json.loads(op.image_list)
							else:
								op.images = []
							# if check_stock:

								# check = next((x for x in combination if x.attribute_id == '{0}\n'.format(op.name)), None)
								# if check:
								# 	op.stock = (check.stock or 0)
								# 	if op.stock and int(op.stock) > 0:
								# 		has_attr_stock = True
				# Inserted by suguna on 05/08/20
				if show_attributes==1:
					x.variant_price = validate_attributes_stock(x.name,attribute_ids,attribute,x.minimum_order_qty,add_qty=None)
					x.attribute_price = attribute_price
					x.attribute_old_price = attribute_old_price
				# End
				x.have_attribute = 1
				x.product_attributes = product_attributes
			else:
				x.have_attribute = 0
				x.product_attributes = product_attributes
			x.has_attr_stock = has_attr_stock
			product_variant = frappe.db.sql('''select * from `tabProduct Variant Combination` where parent = %(parent)s''',{'parent': x.name}, as_dict=1)
			for v_comb in product_variant:
				v_comb.video_list = frappe.db.sql("""select * from `tabProduct Attribute Option Video` where option_id = %(option_id)s""", {"option_id": v_comb.name},as_dict = 1)
			x.product_variant = product_variant
			# product_specification = frappe.db.get_all('Product Specification Attribute Mapping',
			# 					  fields=['specification_attribute', 'options', 'name'],
			# 					  filters={'parent': x.name}, limit_page_length=50)

			# x.product_specification = product_specification
			specification_group = []
			specification_attribute = frappe.db.sql_list('''select distinct sam.spec_group_name,sg.display_order from `tabSpecification Group` sg inner join `tabProduct Specification Attribute Mapping` sam on sg.name=sam.spec_group_name1 where sam.parent=%(name)s order by sg.display_order''',{'name':x.name})
			if specification_attribute:
				for item in specification_attribute:
					groups = frappe.db.get_all('Product Specification Attribute Mapping',fields=['specification_attribute','options'], filters={"parent":x.name,'spec_group_name':item},order_by='idx')
					specification_group.append({"name":item, "groups":groups})
			else:
				groups = frappe.db.get_all('Product Specification Attribute Mapping',fields=['specification_attribute','options'], filters={"parent":x.name},order_by='idx')
				if groups:
					specification_group.append({"name":"", "groups":groups})
					
			x.product_specification = specification_group
			if not x.product_brand:
				x.product_brand = ''
			else:
				if len(x.product_brand) > 30:
					x.product_brand = x.product_brand[:15] + '...'
			highlights = frappe.db.get_all('Highlights', fields=['highlights'], filters={'parent': x.name})
			x.highlights = highlights
			if x.return_description:
				x.return_policy = x.return_description
			if x.tax_category:
				tax_template = frappe.get_doc('Product Tax Template', x.tax_category)
				x.tax_template = tax_template
			if current_category:
				x.products_per_row = frappe.db.get_value('Product Category', current_category, 'products_per_row_in_list')
			if x.category:
				category1 = frappe.get_doc('Product Category', x.category)
				if category1:
					x.category1 = category1.type_of_category
					x.show_attributes_inlist = show_attributes
			product_reviews = frappe.db.sql('''select ifnull(count(*), 0) as review_count,ifnull(avg(rating), 0) as rating from `tabProduct Review` where product=%(product)s''', {'product': x.name}, as_dict=1)
			if product_reviews:
				x.rating = product_reviews[0].rating
				x.review_count = product_reviews[0].review_count
			# product_video = frappe.db.get_all('Product Video', fields=['display_order', 'video_link', 'name'], filters={'parent': x.name}, order_by='display_order')
			product_video = frappe.db.get_all('Product Video', fields=['display_order', 'video_link', 'name', 'video_type'], filters={'parent': x.name}, order_by='display_order')
			x.product_video = product_video
			x.product_tag = frappe.db.get_value('Product', x.name, 'product_tag')
			if x.product_tag:
				tags = json.loads(x.product_tag)
				x.product_tags = frappe.db.get_all('Product Tag', filters={'name': ('in', tags)}, fields=['title', 'icon'])
			if x.restaurant:
				business = frappe.get_doc('Business', x.restaurant)
				x.business_route = business.route
				x.business_logo = business.restaurant_logo
			installed_apps=frappe.db.sql(''' select * from `tabModule Def` where app_name='book_shop' ''',as_dict=True)
			if len(installed_apps)>0:
				x.book_type=x.book_type
				x.published_year=x.published_year
				x.number_of_pages=x.number_of_pages
				x.author_name=x.author_name
				x.author_route=x.author_route
				x.publisher_name=x.publisher_name
				x.publisher_route=x.publisher_route
			# By kartheek for getting custom fields
			custom_values = None
			if catalog_settings.display_custom_fields == 1:
				if frappe.db.get_all("Custom Field",filters={"dt":"Product"}):
					custom_fields = frappe.db.sql('''SELECT fieldname FROM `tabCustom Field` WHERE dt = "Product" AND fieldtype<> "Table" AND fieldtype<> "Section Break" AND fieldtype<> "Column Break" AND fieldtype<> "HTML"  AND fieldtype<> "Check" AND fieldtype<> "Text Editor" ''',as_dict=1)
					query = "SELECT "
					for field in custom_fields:
						query += field.fieldname+","
					query = query[:-1]
					query += " FROM `tabProduct` WHERE name='{0}'".format(x.name)
					columns = ','.join([str(field.fieldname) for field in custom_fields])
					custom_values = frappe.db.sql(query,as_dict=1)
					if custom_values:
						custom_values = custom_values[0]
			x.custom_values = custom_values
			
			# By kartheek for getting custom fields
	return product


def get_child_categories(category):
	try:
		if category:
			lft, rgt = frappe.db.get_value('Product Category', category, ['lft', 'rgt'])
			# if lft != "lft" and rgt != "rgt":
			return frappe.db.sql('''select name from `tabProduct Category` where is_active = 1 and disable_in_website = 0 and lft >= {lft} and rgt <= {rgt}'''.format(lft=lft, rgt=rgt), as_dict=1)
		# else:
		# 	return frappe.db.sql('''select name from `tabProduct Category` where is_active = 1 and disable_in_website = 0 and parent_product_category = %(parent_categiry)s '''.format(parent_categiry=category), as_dict=1)

		# return frappe.db.get_all('Product Category', fields=['name'], filters={'is_active': 1, 'parent_product_category': category}, limit_page_length=100)
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store.ecommerce_business_store.api.get_child_categories')
