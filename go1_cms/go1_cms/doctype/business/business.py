# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json, os, string, random
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils.nestedset import NestedSet
from frappe import _, scrub
from urllib.parse import unquote
from frappe.utils import now, getdate
from frappe.utils.momentjs import get_all_timezones
from frappe.core.doctype.domain_settings.domain_settings import get_active_domains
from datetime import datetime, date
from go1_cms.utils.setup import get_settings_value_from_domain, get_settings_from_domain
from go1_cms.go1_cms.api import check_domain
from frappe.query_builder import DocType

class Business(WebsiteGenerator, NestedSet):
	nsm_parent_field = 'parent_business'
	def autoname(self):
		# to override autoname of WebsiteGenerator
		from frappe.model.naming import make_autoname
		if self.parent_business:
			self.naming_series = frappe.db.get_value('Business', self.parent_business, 'abbr')
		self.name = make_autoname(self.naming_series + '.#####', doc=self)

	def validate(self):
		self.lft = ""
		self.rgt = ""
		self.validate_email_type(self.contact_email)
		# validate_zip(self.zip_code)
		# if not self.abbr:
		restaurant_name = self.restaurant_name.replace('(','').replace(')','')
		name_parts = restaurant_name.split()
		if self.get('__islocal') or not self.abbr:
			abbr = ''.join([c[0] for c in name_parts]).upper()	
			check_abbr = frappe.db.sql('''select name,abbr from `tabBusiness` where abbr=%(abbr)s''',{'abbr':abbr},as_dict=1)
			car=self.id_generator()
			if len(check_abbr)>0:
				self.abbr=abbr+car+str(len(check_abbr))
			else:
				self.abbr=abbr
			self.abbr = self.abbr.replace('&', '')
		if not self.route:
			route=self.scrub(self.restaurant_name+'-'+self.abbr)	
			self.route = route	
		address=''
		maps = frappe.get_single('Google Settings')
		if maps.enable:	
			if self.business_address:
				address += self.business_address+','
			if self.city:
				address += self.city + ','
			if self.state:
				address += self.state + ' '
			if self.zip_code:
				address += self.zip_code		
			validate_geo_location(self, address)
		if self.show_in_website :
			address=''
			if self.business_address:
				address += self.business_address+','
			if self.city:
				address += self.city + ','
			if self.zip_code:
				address += self.zip_code
				check_website = frappe.db.get_all('Site Settings', filters={'business': self.name}, fields=['business', 'theme', 'home_page', 'domain_name'])
				if check_website and check_website[0].theme:
					web_theme = frappe.get_doc('Web Theme', check_website[0].theme)
					web_theme.footer_address = address
					web_theme.footer_phone = self.contact_number
					web_theme.footer_email = self.contact_email
					web_theme.save(ignore_permissions=True)
				

		# if not self.random_id:
		# 	from frappe.utils import random_string
		# 	self.random_id = random_string(12)
		# if check_domain('multi_vendor'):
		# 	get_shop_user = frappe.db.get_all('Shop User',filters={'restaurant':self.name},fields=['*'])
		# 	if not get_shop_user:
		# 		current_year = datetime.date.today().year
		# 		rest_name = self.restaurant_name.title()
		# 		password = "#"+rest_name.replace(' ', '')+"@"+str(current_year)+"#"
		# 		shop_user = frappe.new_doc('Shop User')
		# 		shop_user.first_name = 'Admin'
		# 		shop_user.mobile_no = self.contact_number
		# 		shop_user.email = self.contact_email
		# 		shop_user.restaurant = self.name
		# 		shop_user.set_new_password = password
		# 		shop_user.save(ignore_permissions=True)


		if not self.meta_title:
			self.meta_title = self.restaurant_name
		if not self.meta_keywords:
			self.meta_keywords = self.restaurant_name.replace(" ", ", ")
		if not self.meta_description:
			self.meta_description = "About: {0}".format(self.restaurant_name)

	def after_insert(self):
		if check_domain('saas'):
			frappe.defaults.add_default('business_setup', '[]', self.name, 'Business')

	def validate_email_type(self, email):
		from frappe.utils import validate_email_address
		validate_email_address(email.strip(), True)

	def id_generator(self,size=4, chars=string.ascii_uppercase):
		return ''.join(random.choice(chars) for _ in range(size))

	def get_context(self, context):
		from go1_cms.go1_cms.api import check_domain
		context.brand_name = self
	
		context.template = 'templates/pages/businessdetail.html'
		
		try:
			domain = frappe.get_request_header('host')
		except Exception as e:
			domain = None

		if domain and not frappe.db.get_value('Site Settings', domain):
			if not self.publish_in_market_place:
				frappe.local.flags.redirect_location = '/404'
				raise frappe.Redirect
		elif domain and frappe.db.get_value('Site Settings', domain):
			business = frappe.db.get_value('Site Settings', domain, 'business')
			if business != self.name:
				frappe.local.flags.redirect_location = '/404'
				raise frappe.Redirect
			_ord_type = frappe.form_dict.type
		allow_review = 0
		if frappe.session.user != 'Guest':
			allow_review = 1
		else:
			if context.catalog_settings.allow_anonymous_users_to_write_product_reviews:
				allow_review = 1
		context.allow_review = allow_review
		context.meta_title = self.meta_title if self.meta_title else context.catalog_settings.meta_title
		context.meta_description = self.meta_description if self.meta_description else context.catalog_settings.meta_description
		context.meta_keywords = self.meta_keywords if self.meta_keywords else context.catalog_settings.meta_keywords

	

	def insert_sample_records(self):
		insert_default_data(self.name, self.restaurant_name)
		return {'status': 'Success'}

	def on_trash(self):
		NestedSet.on_update(self)
	


def update_thumb(item,list_size):
	file_doc = frappe.get_doc("File", {
		"file_url": item.business_image,
		"attached_to_doctype": "Business",
		"attached_to_name": item.parent
	})
	image_file=item.business_image.split('.')
	file_doc.make_thumbnail(set_as_thumbnail=False,width=list_size,height=list_size,suffix=str(list_size)+"x"+str(list_size))
	item.thumbnail=image_file[0]+"_"+str(list_size)+"x"+str(list_size)+"."+image_file[1]
	item.thumbnail=file_doc.thumbnail_url
	item.save()

@frappe.whitelist()
def validate_geo_location(self,address):
	try:
		if not self.latitude or not self.longitude:				
			from go1_cms.go1_cms.api import get_geolocation
			location_data=get_geolocation(address)
			if location_data:
				self.latitude=location_data['latitude']
				self.longitude=location_data['longitude']
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.business.validate_geo_location") 
	
@frappe.whitelist()
def get_timeZone():
	try:
		return {
			"timezones": get_all_timezones()
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.business.add_on.get_timeZone") 
	

def get_permission_query_conditions(user):
	try:
		if not user: user = frappe.session.user

		if "System Manager" in frappe.get_roles(user):
			return None
		else:
			user=frappe.db.get_all('Shop User',filters={'name':user},fields=['*'])
			if user:
				return """(`tabBusiness`.name = '{restaurant}')"""\
					.format(restaurant=user[0].restaurant)
			else:
				return None
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.business.get_permission_query_conditions") 
	

@frappe.whitelist()
def get_print_formats():	
	try:
		print_format = DocType('Print Format')
		result = (
			frappe.qb.from_(print_format)
			.select(print_format.name)
			.where(print_format.doc_type == "Order")
		).run(as_dict=True)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.business.get_print_formats") 
	
@frappe.whitelist()
def get_sorted_columns(sort_by):
	try:
		switcher = {
			"Relevance": "relevance",
			"Name: A to Z": "name_asc",
			"Name: Z to A": "name_desc",
			"Price: Low to High": "price_asc",
			"Price: High to Low": "price_desc",
			"Newest Arrivals": "creation desc",
			"Date: Oldest first": "creation asc"
		 
		}
		return switcher.get(sort_by, "Invalid value")
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.product_brand.get_sorted_columns") 
	

@frappe.whitelist()
def get_all_amenities(category_list):
	condition=''
	if category_list:
		condition=' where c.name in ({0})'.format(category_list)
	amenity_group=frappe.db.sql('''select distinct ac.amenity_group from `tabAmenities Category Mapping` ac inner join `tabProduct Category` c on c.name=ac.parent {condition} order by ac.amenity_group'''.format(condition=condition),as_dict=1)
	if amenity_group:
		for item in amenity_group:
			child_condition=''
			if condition=='':
				child_condition=' where ac.amenity_group="%s"' % item.amenity_group
			else:
				child_condition=condition+' and ac.amenity_group="%s"' % item.amenity_group
			item.amenities=frappe.db.sql('''select ac.amenity from `tabAmenities Category Mapping` ac inner join `tabProduct Category` c on c.name=ac.parent {condition} order by ac.amenity'''.format(condition=child_condition),as_dict=1)
	return amenity_group

@frappe.whitelist()
def get_children_new(doctype, parent=None, is_root=False, is_tree=False):
	condition = ''

	if is_root:
		parent = ""
	if parent:
		condition = ' where parent_business = "{0}"'.format(frappe.db.escape(parent))	

	business = frappe.db.sql("""
		select
			name as value, restaurant_name as title,
			exists(select name from `tabBusiness` where parent_business=b.name) as expandable
		from
			`tabBusiness` b
		{condition} order by name"""
		.format(condition=condition),  as_dict=1)
	
	return business

@frappe.whitelist()
def add_branch(**kwargs):
	doc = frappe.get_doc('Business',kwargs.get('parent_business'))
	doc.name = None
	doc.contact_person = kwargs.get('contact_person')
	doc.business_phone = kwargs.get('business_phone')
	doc.contact_number = kwargs.get('contact_number')
	doc.contact_email = kwargs.get('contact_email')
	doc.business_address = kwargs.get('business_address')
	doc.city = kwargs.get('city')
	doc.parent_business = kwargs.get('parent_business')
	doc.is_group = kwargs.get('is_group')
	doc.restaurant_name = kwargs.get('business_name')
	doc.abbr = None
	doc.rgt = None
	doc.lft = None
	doc.old_parent = None
	doc.save(ignore_permissions=True)
	assign_branch_head_permissions(kwargs.get('parent_business'), doc.name)
	return doc.name

def assign_branch_head_permissions(parent_business, business):
	shop_users = frappe.db.get_all('Shop User', filters={'role': 'Manager', 'restaurant': parent_business})
	for user in shop_users:
		frappe.permissions.add_user_permission('Business', business, user.name, ignore_permissions=True)

def get_query_condition(user):
	if not user: user = frappe.session.user
	if "System Manager" in frappe.get_roles(user):
		return None

	if "Vendor" in frappe.get_roles(user):
		shop_user = frappe.db.get_all('Shop User',filters={'name':user},fields=['restaurant'])
		if shop_user and shop_user[0].restaurant:
			return """(`tabBusiness`.name = '{business}' or `tabBusiness`.parent_business = '{business}')""".format(business=shop_user[0].restaurant)
		else:
			return """(`tabBusiness`.owner = '{user}')""".format(user=user)

def has_permission(doc, user):
	if "System Manager" in frappe.get_roles(user):
		return True
	if "Vendor" in frappe.get_roles(user):
		shop_user = frappe.db.get_all('Shop User',filters={'name':user},fields=['restaurant'])
		if shop_user:
			if shop_user[0].restaurant in [doc.name, doc.parent_business]:
				return True
		return False

	return True

@frappe.whitelist(allow_guest=True)
def get_business_reviews(business, page_no=1, page_len=10, as_html=0):
	start = int(page_no) * int(page_len)
	reviews = frappe.db.sql('''select * from `tabBusiness Reviews` where is_approved=1 and  business = %(business)s limit {0}, {1}'''.format(start, page_len), {'business': business}, as_dict=1)
	if as_html:
		template = frappe.get_template("/templates/pages/reviewlist.html")
		return template.render({"reviews": reviews})

	return reviews

@frappe.whitelist(allow_guest=True)
def insert_dummy_data(checked_business, business, business_name):
	import re
	vertical_name = re.sub('[^a-zA-Z0-9 ]', '', checked_business).lower().replace(' ','_')
	vertical_name1 = vertical_name+".json"
	path = frappe.get_module_path("go1_cms")
	path_parts=path.split('/')
	path_parts=path_parts[:-1]
	url='/'.join(path_parts)
	if not os.path.exists(os.path.join(url,'verticals')):
		frappe.create_folder(os.path.join(url,'verticals'))
	# file_path = os.path.join(url, 'verticals', vertical_name1)
	
	file_path = os.path.join(url, 'verticals', vertical_name1)
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			out = json.load(f)
		for i in out:
			try:
				i['business'] = business
				i['restaurant'] = business
				i['business_name'] = business_name
				
				frappe.get_doc(i).insert(ignore_links=True, ignore_mandatory=True)
			except Exception as e:
				frappe.log_error(frappe.get_traceback(),'insert_dummy_data')   
	return {'status': 'Success'}

@frappe.whitelist()
def get_website_details(business):
	web_list = frappe.db.get_all('Site Settings', filters={'business': business})
	if web_list:
		return {'has_web': 1}

	return {'has_web': 0}

