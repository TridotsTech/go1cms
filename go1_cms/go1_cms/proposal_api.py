
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals,print_function

import json
import frappe
import frappe.client
from frappe.utils.response import build_response
from frappe import _
import json
from six import iteritems, string_types
from datetime import datetime
from frappe.utils import flt, cint, getdate, get_datetime, get_time, make_filter_tuple, get_filter, add_to_date
from cryptography.fernet import Fernet, InvalidToken
try:
	from HTMLParser import HTMLParser
except Exception:
	from html.parser import HTMLParser
# from content_management_system.content_management_system.utils import get_special_tags

@frappe.whitelist(allow_guest = True)
def get_website_context(context):
	h = HTMLParser()
	social_tracking_codes = frappe.get_single('Social Tracking Codes')
	if social_tracking_codes.google_site_verification:
		site_verification = frappe.render_template('{{metacode}}',{'metacode':h.unescape(social_tracking_codes.google_site_verification)})
	else:
		site_verification=""
	context.site_verification = site_verification
	header_script = None
	if social_tracking_codes.header_script:
		header_script = social_tracking_codes.header_script
	context.header_script = header_script
	layout_settings=frappe.get_single('Layout Settings')
	pagejs = unescape(layout_settings.page_js)
	context.pagejs_function = pagejs
	if layout_settings.header_template:
		default_header_template = frappe.db.get_value("Header Template", layout_settings.header_template, "route")
	else:
		default_header_template = "templates/layout/basenavbar.html"
	if layout_settings.footer_template:
		default_footer_template = frappe.db.get_value("Footer Template", layout_settings.footer_template, "route")
	else:
		default_footer_template = "templates/layout/basefooter.html"
	context.default_header_template = default_header_template 
	context.default_footer_template = default_footer_template 
	context.layout_settings = layout_settings
	#builder page details
	get_pagebuilder_context(context)
	#social login settings
	update_context(context)

def get_pagebuilder_context(context, doc=None):
	path = frappe.local.request.path
	context.path = path
	if doc:
		page_builder = frappe.get_all("Page Builder", fields=["name"], filters= {"name":doc.name, "is_active":1})
	else:
		pageroute = get_website_rules(context.path)
		if pageroute:
			page_route = pageroute
		else:
			path = path.strip('/')
			word = path.split('/')
			page_route = word[0]
		if page_route and page_route!="/":
			page_builder = frappe.get_all("Page Builder", fields=["name"], filters= {"name":page_route, "is_active":1})
		else:
			page_builder = frappe.get_all("Page Builder", fields=["name"], filters= {"name":"homepage", "is_active":1})
	if page_builder:
		page_component = frappe.get_all("Page Component", fields = ['component'], filters = {"parent":page_builder[0].name}, order_by="idx asc")		
		if page_component:
			for item in page_component:
				dynamic_list = frappe.get_all("Section", fields = ["*"], filters = {"name":item.component,"content_type":"Dynamic","generate_as_jinja":1})
				for section in dynamic_list:	
					if section.section_template and section.content_type=="Dynamic":
						content = frappe.get_list("Page Content", fields=['content_key', 'content'], filters={"parent":section.section_template})
						for cont in content:
							context[cont.content_key] = cont.content
					if section.filters_json:
						filters = json.loads(section.filters_json)
					if section.ref_doc_fields:
						field_list = json.loads(section.ref_doc_fields)
						pages_list = list(set(field_list))
						fields_list = ', '.join(['' + str(i) + '' for i in pages_list])
					else:
						fields_list = "*"

					groupby_con = ""
					if section.get('group_by_fields'):
						groupby_con = "group by "+groupby_condition(section.group_by_fields)
					
					orderby_con = ""
					if section.order_by_fields:
						orderby_con = orderby_condition(section.order_by_fields,section.orderby_type)
					else:
						orderby_con = "name asc"
					condition = ''
					c_condition = ''
					if section.number_of_list:
						limit = section.number_of_list
					else:
						limit = 3
					condition = convert_json_conditions(filters, section.reference_doctype, condition)
					frappe.log_error(condition, "---condition---")
					query = '''select {fields_list} from `tab{doctype}` where `tab{doctype}`.name != "" {condition} {groupby_con} order by {orderby_con} limit {limit}'''.format(fields_list=fields_list, doctype=section.reference_doctype, condition=condition, groupby_con=groupby_con, orderby_con = orderby_con, limit = limit)					
					# query = '''select {fields_list} from `tab{doctype}` where `tab{doctype}`.name != "" {condition} order by name asc limit {limit}'''.format(fields_list=fields_list, doctype=section.reference_doctype, condition=condition, limit = limit)
					# frappe.log_error(query, "query")
					if frappe.db.get_value("DocField", {"parent": "Section","fieldname": "enable_custom_query"}):
						if section.enable_custom_query ==1:
							
							query = section.custom_query
							section_list = frappe.db.sql(query,as_dict=1)
							
						else:
							section_list = frappe.db.sql(query,as_dict=1)
					else:
						section_list = frappe.db.sql(query,as_dict=1)
					context_value = section.context_name	
				
					context[context_value] = section_list
				static_list = frappe.get_all("Section", fields = ["section_type, section_template, content_type, reference_doctype, number_of_list, generate_as_jinja, context_name, filters_json, ref_doc_fields"], filters = {"name":item.component,"content_type":"Static","generate_as_jinja":1})
				
				for s_section in static_list:
					if s_section.section_template and s_section.content_type=="Static":
						
						contents = frappe.get_list("Page Content", fields=['content_key', 'content'], filters={"parent":s_section.section_template})
						
						for cont in contents:
							context[cont.content_key] = cont.content
	# get_special_tags(context)				
	
@frappe.whitelist(allow_guest = True)
def orderby_condition( orderby_fields, orderby_type=None):
	orderby_con = ""
	if orderby_fields:
		orderby_field_list = json.loads(orderby_fields)
		order_list = list(set(orderby_field_list))
		orderby_list = ', '.join(['' + str(i) + '' for i in order_list])
	else:
		orderby_list = "name"
	if orderby_type:
		if orderby_type == "Ascending":
			orderby_type = "asc"
		if orderby_type == "Descending":
			orderby_type = "desc"
		orderby_con += orderby_list + " "+ orderby_type
	else:
		orderby_type = "asc"
	return orderby_con

@frappe.whitelist(allow_guest = True)
def groupby_condition(groupby_fields):
        groupby_con = ""
        if groupby_fields:
                groupby_field_list = json.loads(groupby_fields)
                group_list = list(set(groupby_field_list))
                groupby_list = ', '.join(['' + str(i) + '' for i in group_list])
        groupby_con += groupby_list
        return groupby_con

@frappe.whitelist(allow_guest = True)
def update_context(context):
	#web settings
	web_settings=frappe.get_single('Website Settings')
	context.WebsiteSettings=web_settings
	
	# contact settings
	contact_settings=frappe.get_doc('Contact Settings','Contact Settings')
	context.contact_settings=contact_settings
	context.currenturl = frappe.local.request.url 
	context.csrf_token=frappe.local.session.data.csrf_token if frappe.local.session.data.csrf_token else ''
	#social trackings
	tracking_codes= frappe.get_single('Social Tracking Codes')
	h = HTMLParser()
	script_codes=[]
	default_columns=['owner','name','modified_by','_meta','creation','doctype','modified','idx','docstatus','facebook_page_id', 'google_site_verification']
	for attr, value in tracking_codes.__dict__.iteritems():
		if not attr in default_columns:
			if value:
				script_codes.append(h.unescape(value))
	context.tracking_codes=script_codes
	context.fb_page_id=tracking_codes.facebook_page_id
	context.website_theme_setting= frappe.get_doc('Website Theme Setting')
	google_map_settings=frappe.get_doc('Google Maps Settings','Google Maps Settings')
	context.google_maps=google_map_settings
	path = frappe.local.request.path
	pageroute = get_website_rules(context.path)
	if pageroute:
		page_route = pageroute
	else:
		path = path.strip('/')
		word = path.split('/')
		page_route = word[0]
	if page_route:
		seo=frappe.db.get_all('Page SEO',filters={'page_route':page_route},fields=['meta_title','meta_description','meta_keywords'])
		if seo:
			context.meta_title=seo[0].meta_title
			context.meta_description=seo[0].meta_description
			context.meta_keywords=seo[0].meta_keywords
	else:
		seo=frappe.db.get_all('Page SEO',filters={'page_route':"homepage"},fields=['meta_title','meta_description','meta_keywords'])
		if seo:
			context.meta_title=seo[0].meta_title
			context.meta_description=seo[0].meta_description
			context.meta_keywords=seo[0].meta_keywords

#convert json to query
@frappe.whitelist(allow_guest = True)
def convert_json_conditions(filters, doctype, condition):
	try:
		if filters:
			for f in filters:
				fl = get_filter_condition(f, doctype)
				if fl.operator:
					cond = prepare_filter_condition(doctype, f, ignore_ifnull=True)
					if cond:
						condition += ' and {0}'.format(cond)
		return condition
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.convert_json_conditions")

@frappe.whitelist(allow_guest = True)
def get_filter_condition(f, doctype):
	from frappe.model import default_fields, optional_fields
	doctype = doctype
	if isinstance(f, dict):
		key, value = next(iter(f.items()))
		f = make_filter_tuple(doctype, key, value)
	if len(f) == 3:
		f = (doctype, f[0], f[1], f[2])

	elif len(f) > 4:
		f = f[0:4]
	print(f)
	f = frappe._dict(doctype=f[0], fieldname=f[1], operator=f[2], value=f[3])

	if not f.operator:
		# if operator is missing
		f.operator = "="

	if f.doctype and (f.fieldname not in default_fields + optional_fields):
		# verify fieldname belongs to the doctype
		meta = frappe.get_meta(f.doctype)
		if not meta.has_field(f.fieldname):
			# try and match the doctype name from child tables
			for df in meta.get_table_fields():
				if frappe.get_meta(df.options).has_field(f.fieldname):
					f.doctype = df.options
					break
	return f

def prepare_filter_condition(doctype, f, ignore_ifnull):
	"""Returns a filter condition in the format:

			ifnull(`tabDocType`.`fieldname`, fallback) operator "value"
	"""

	f = get_filter(doctype, f)

	tname = ('`tab' + f.doctype + '`')
	# if not tname in self.tables:
	# 	self.append_table(tname)

	if 'ifnull(' in f.fieldname:
		column_name = f.fieldname
	else:
		column_name = '{tname}.{fname}'.format(tname=tname,
			fname=f.fieldname)

	can_be_null = True

	# prepare in condition
	if f.operator.lower() in ('in', 'not in'):
		values = f.value or ''
		if not isinstance(values, (list, tuple)):
			values = values.split(",")

		fallback = "''"
		value = (frappe.db.escape((v or '').strip(), percent=False) for v in values)
		value = '("{0}")'.format('", "'.join(value))
	else:
		df = frappe.get_meta(f.doctype).get("fields", {"fieldname": f.fieldname})
		df = df[0] if df else None

		if df and df.fieldtype in ("Check", "Float", "Int", "Currency", "Percent"):
			can_be_null = False

		if f.operator.lower() == 'between' and \
			(f.fieldname in ('creation', 'modified') or (df and (df.fieldtype=="Date" or df.fieldtype=="Datetime"))):

			value = get_between_date_filter(f.value, df)
			fallback = "'0000-00-00 00:00:00'"

		elif df and df.fieldtype=="Date":
			value = getdate(f.value).strftime("%Y-%m-%d")
			fallback = "'0000-00-00'"

		elif (df and df.fieldtype=="Datetime") or isinstance(f.value, datetime):
			value = get_datetime(f.value).strftime("%Y-%m-%d %H:%M:%S.%f")
			fallback = "'0000-00-00 00:00:00'"

		elif df and df.fieldtype=="Time":
			value = get_time(f.value).strftime("%H:%M:%S.%f")
			fallback = "'00:00:00'"

		elif f.operator.lower() in ("like", "not like") or (isinstance(f.value, string_types) and
			(not df or df.fieldtype not in ["Float", "Int", "Currency", "Percent", "Check"])):
				value = "" if f.value==None else f.value
				fallback = '""'

				if f.operator.lower() in ("like", "not like") and isinstance(value, string_types):
					# because "like" uses backslash (\) for escaping
					value = value.replace("\\", "\\\\").replace("%", "%%")

		else:
			# value = flt(f.value)
			value = f.value
			fallback = 0
		print(value)
		# put it inside double quotes
		if isinstance(value, string_types) and not f.operator.lower() == 'between':
			value = '{0}'.format(frappe.db.escape(value, percent=False))
	if (ignore_ifnull
		or not can_be_null
		or (f.value and f.operator.lower() in ('=', 'like'))
		or 'ifnull(' in column_name.lower()):
		condition = '{column_name} {operator} {value}'.format(
			column_name=column_name, operator=f.operator,
			value=value)
	else:
		condition = 'ifnull({column_name}, {fallback}) {operator} {value}'.format(
			column_name=column_name, fallback=fallback, operator=f.operator,
			value=value)
	return condition



@frappe.whitelist(allow_guest=True)
def insert_enquiry(name,email,phone,message,subject=None):
	try:
		enquiry=frappe.new_doc('Contact Enquiry')
		enquiry.user_name=name
		enquiry.email=email
		enquiry.message=message
		if subject:
			enquiry.subject=subject
		enquiry.phone=phone
		enquiry.save(ignore_permissions=True)
		
		return enquiry
		# return enquiry.__dict__
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.insert_enquiry")

@frappe.whitelist(allow_guest=True)
def insert_doc(doc):
	try:
		from six import string_types
		if isinstance(doc, string_types):
			doc = json.loads(doc)
		if doc.get("parent") and doc.get("parenttype"):
			# inserting a child record
			parent = frappe.get_doc(doc.get("parenttype"), doc.get("parent"))
			parent.append(doc.get("parentfield"), doc)
			parent.save(ignore_permissions=True)
			return parent.as_dict()
		else:
			doc = frappe.get_doc(doc).insert(ignore_permissions=True)
			return doc.as_dict()
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.insert_doc")

@frappe.whitelist(allow_guest=True)
def update_sections_doc_json(docs,ref_doc=None,ref_name=None):
	try:
		if docs:
			update_doc = frappe.get_doc(ref_doc, ref_name)
			update_doc.template_keys = docs
			update_doc.save(ignore_permissions=True)
			return {"message": "success"}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.bulk_update_doc")

@frappe.whitelist(allow_guest=True)
def bulk_update_doc(docs,ref_doc=None,ref_name=None):
	try:
		if docs:
			if isinstance(docs, string_types):
				docs = json.loads(docs)
			for doc in docs:
				update_doc(doc)
			if ref_doc and ref_name:
				frappe.get_doc(ref_doc, ref_name).save(ignore_permissions=True)
			return {"message": "success"}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.bulk_update_doc")

@frappe.whitelist(allow_guest=True)
def update_doc(doc):
	try:
		from six import string_types
		if isinstance(doc, string_types):
			doc = json.loads(doc)
		keys = doc.keys()
		update_doc = frappe.get_doc(doc.get('doctype'), doc.get('name'))
		for key in keys:
			setattr(update_doc, key, doc.get(key))
		update_doc.save(ignore_permissions=True)
		return update_doc.as_dict()
	except Exception as e:
		return e

@frappe.whitelist(allow_guest = True)
def insert_newsletter(data):
	try:
		subcriber = frappe.new_doc("Email Group Member")
		subcriber.email_group = "NewsLetter Group"
		subcriber.email = data
		subcriber.insert(ignore_permissions = True)
		return True
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.insert_newsletter")

@frappe.whitelist()
def get_fields_label(doctype):
	try:
		fields=[
			{
				"fieldname":"name",
				"label":"Name",
				"fieldtype":"Link",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"creation",
				"label":"Created On",
				"fieldtype":"Datetime",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"modified",
				"label":"Modified On",
				"fieldtype":"Datetime",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"owner",
				"label":"Created By",
				"fieldtype":"Link",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"modified_by",
				"label":"Modified By",
				"fieldtype":"Link",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"docstatus",
				"label":"Document Status",
				"fieldtype":"Int",
				"hidden":"0",
				"permlevel":0
			}
		]
		fields+=[{"fieldname": df.fieldname or "", "label": _(df.label or ""), "fieldtype": _(df.fieldtype or ""), "hidden": _(df.hidden), "permlevel": _(df.permlevel)}
			for df in frappe.get_meta(doctype).get("fields")]
		return fields
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.get_fields_label")

@frappe.whitelist()
def get_orderby_fields(doctype):
	try:
		fields=[
			{
				"fieldname":"name",
				"label":"Name",
				"fieldtype":"Link",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"creation",
				"label":"Created On",
				"fieldtype":"Datetime",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"modified",
				"label":"Modified On",
				"fieldtype":"Datetime",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"owner",
				"label":"Created By",
				"fieldtype":"Link",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"modified_by",
				"label":"Modified By",
				"fieldtype":"Link",
				"hidden":"0",
				"permlevel":0
			},
			{
				"fieldname":"docstatus",
				"label":"Document Status",
				"fieldtype":"Int",
				"hidden":"0",
				"permlevel":0
			}
		]
		fields+=[{"fieldname": df.fieldname or "", "label": _(df.label or ""), "fieldtype": _(df.fieldtype or ""), "hidden": _(df.hidden), "permlevel": _(df.permlevel)}
			for df in frappe.get_meta(doctype).get("fields")]
		return fields
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.get_orderby_fields")

def get_website_rules(page_route):
	try:
		rules = frappe.get_hooks("website_route_rules")
		if rules:
			for route in rules:
				if page_route == route["from_route"]:
					return route["to_route"]
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.get_website_rules")

@frappe.whitelist()
def unescape(s):
	try:
		if s:
			s = s.replace("&lt;", "<")
			s = s.replace("&gt;", ">")
			# this has to be last:
			s = s.replace("&amp;", "&")
		return s
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.unescape")

@frappe.whitelist()
def get_template_details(template):
	try:
		if template:
			templates = frappe.db.get_all("Page Section",fields=["*"],filters={"name": template})[0]
			keys = frappe.db.get_all("Page Content", fields=["name", "idx", "field_label", "content_key", "field_type", "select_type", "content"], filters={"parent": template}, order_by="idx asc")
			return {"template":templates, "keys": keys}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.get_template_details")

@frappe.whitelist(allow_guest=True)
def get_site_template_folder(url):
	import frappe, os, re, json
	import tldextract
	temp_path = ""
	cur_domain = frappe.local.request.host_url.split('/')[-2:][0]
	info = tldextract.extract(cur_domain)
	subdomain=info.subdomain.split(".")[-1:][0]
	cur_domain = info.domain
	if subdomain and subdomain!="www":
		cur_domain = subdomain+"_"+info.domain
	if cur_domain:
		if not os.path.exists(os.path.join(url, 'templates/pages', cur_domain)):
			frappe.create_folder(os.path.join(url, 'templates/pages', cur_domain))
		temp_path = os.path.join(url,'templates/pages', cur_domain)
	else:
		temp_path = os.path.join(url,'templates/pages')
	return temp_path

@frappe.whitelist(allow_guest=True)
def get_template_folder(url, temp=0):
	try:
		import frappe, os, re, json
		temp_path = ""
		cur_domain = frappe.local.request.host_url.split('/')[-2:][0]
		tem_folder = frappe.db.get_value("Site Domain", cur_domain, "site_name")
		base_path = os.path.join(url,'templates/pages')
		if temp==1:
			base_path = 'templates/pages'
		if tem_folder:
			if not os.path.exists(os.path.join(base_path, tem_folder)):
				frappe.create_folder(os.path.join(base_path, tem_folder))
			base_path = os.path.join(base_path, tem_folder)
		return base_path
	except Exception:
		frappe.log_error(frappe.get_traceback(), "api.get_template_folder")
		
@frappe.whitelist(allow_guest=True)
def save_as_template(template, section, custom_css=None):
	if not custom_css:
		custom_css = ""
	doc = frappe.get_doc("Page Section", section)
	doc.page_list = template
	doc.custom_css = custom_css
	doc.save(ignore_permissions=True)


@frappe.whitelist(allow_guest=True)
def get_doc_list(doctype, fields=None, filters=None, order_by=None, limit_start=None, limit_page_length=10, parent=None):
	'''Returns a list of records by filters, fields, ordering and limit

	:param doctype: DocType of the data to be queried
	:param fields: fields to be returned. Default is `name`
	:param filters: filter list by this dict
	:param order_by: Order by this fieldname
	:param limit_start: Start at this index
	:param limit_page_length: Number of records to be returned (default 20)'''
	if frappe.is_table(doctype):
		check_parent_permission(parent, doctype)
	if fields:
		fields=json.loads(fields)
	if filters:
		filters=json.loads(filters)
	if order_by:
		order_by = json.loads(order_by)
        
	return frappe.get_list(doctype, fields=fields, filters=filters, order_by=order_by,
		limit_start=limit_start, limit_page_length=limit_page_length, ignore_permissions=True)

@frappe.whitelist()
def string_to_json(json_string):
    return json.loads(json_string)


@frappe.whitelist()
def generate_token():
	from frappe.utils import random_string, get_url
	key = random_string(32)
	return key

@frappe.whitelist()
def encrypt(url):
	# if len(url) > 100:
		# encrypting > 100 chars will lead to truncation
		# frappe.throw(_('something went wrong during encryption'))

	cipher_suite = Fernet(encode(get_encryption_key()))
	cipher_text = cstr(cipher_suite.encrypt(encode(url)))
	return cipher_text

@frappe.whitelist()
def decrypt(url):
	try:
		cipher_suite = Fernet(encode(get_encryption_key()))
		plain_text = cstr(cipher_suite.decrypt(encode(url)))
		return plain_text
	except InvalidToken:
		# encryption_key in site_config is changed and not valid
		frappe.throw(_('Encryption key is invalid, Please check site_config.json'))

def get_encryption_key():
	from frappe.installer import update_site_config

	if 'encryption_key' not in frappe.local.conf:
		encryption_key = Fernet.generate_key().decode()
		update_site_config('encryption_key', encryption_key)
		frappe.local.conf.encryption_key = encryption_key

	return frappe.local.conf.encryption_key

@frappe.whitelist(allow_guest=True)
def update_proposal_status(proposal, status):
	doc = frappe.get_doc("Proposal", proposal)
	doc.status = status
	doc.save(ignore_permissions=True)
	return doc

