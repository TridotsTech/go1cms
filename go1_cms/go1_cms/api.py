# -*- coding: utf-8 -*-
# Copyright (c) 2019, Tridots and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
import os, re, json, mimetypes
from frappe.utils import getdate, nowdate, now, get_url
from datetime import datetime, timezone
from go1_cms.go1_cms.doctype.web_theme.web_theme import theme_studio_enabled_for
import six

@frappe.whitelist(allow_guest=True)
def get_template_folder(url=None, business=None, temp=0):
	try:
		if not url:
			path = frappe.get_module_path("go1_cms")
			path_parts=path.split('/')
			path_parts=path_parts[:-1]
			url='/'.join(path_parts)
		if business:
			if not os.path.exists(os.path.join(url, 'templates/pages', business)):
				frappe.create_folder(os.path.join(url, 'templates/pages', business))
			temp_path = os.path.join(url,'templates/pages', business)
			if temp==1:
				temp_path = os.path.join('templates/pages', business)	
		else:
			if not os.path.exists(os.path.join(url, 'templates/pages', 'custom_html')):
				frappe.create_folder(os.path.join(url, 'templates/pages', 'custom_html'))
			temp_path = os.path.join(url,'templates/pages', 'custom_html')
			if temp==1:
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
def get_published_pages():
	try:
		pages = frappe.get_all('Web Page Builder', filters={'published': 1}, fields=['name', 'route', 'page_title'])
		return {'pages': pages, 'total_pages': len(pages)}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.api.get_published_pages')
		return {'pages': [], 'error': str(e)}

@frappe.whitelist(allow_guest = True)
def get_scroll_content(route, page_no=0, page_len=3, device_type=None):
	business=None
	context={}
	start = int(page_no) * int(page_len)
	page_builder = frappe.get_doc('Web Page Builder', {"route":route})
	page_section = frappe.get_all("Mobile Page Section", fields=["name", "section", "parent", "section_title"], filters= {"parent":page_builder.name, 'parentfield':'web_section'}, order_by='idx')
	page_section = page_section[start:int(page_len) + int(start)]
	page_template =""
	catalog_settings = get_settings_from_domain('Catalog Settings')
	context['catalog_settings']= catalog_settings
	context['general_settings']=get_settings_from_domain('Business Setting')
	context['currency']= frappe.cache().hget('currency', 'symbol')
	product_box = catalog_settings.product_boxes
	if product_box:
		context['product_box']=frappe.db.get_value('Product Box', product_box, 'route')
	for item in page_section:
		section_template = frappe.db.get_value("Page Section", item.section, ["name", "business", "section_title"], as_dict=True)
		if page_builder.business:
			business=page_builder.business
		temp_path = get_template_folder(business=business, temp=1)
		html_page = section_template.section_title.lower().replace(' ','-') + "-" + (section_template.name).lower().replace(' ','-')
		data_source=get_section_data(item.section, item.parent, device_type)
		context[data_source['context']]= {}
		for key, value in data_source.items():
			context[data_source['context']][key]= value
		template=frappe.render_template(os.path.join(temp_path, (html_page+'.html')), context)
		page_template+=template
	return page_template

@frappe.whitelist(allow_guest = True)
def get_section_data(section, page_builder, device_type):
	from go1_cms.go1_cms.doctype.web_page_builder.web_page_builder import  get_source_doc_data, get_page_section
	page_builder = frappe.get_doc('Web Page Builder', page_builder)
	source_doc, sections= get_source_doc_data(page_builder, device_type)
	# frappe.log_error(source_doc,"source_doc")
	# frappe.log_error(sections,"sections")
	data = get_page_section(source_doc)
	doc = frappe.get_doc("Page Section",section)
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
				rules.append(dict(from_route = '/' + d.route.strip('/'), to_route=d.name))
		for p in frappe.get_all('Web Page Builder', 'name, route', dict(published=1)):
			if p.route:
				html_page = p.route.lower().replace('-','_')
				rules.append(dict(from_route = '/' + html_page, to_route=p.route.strip('/')))
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
							if str(x).lower().replace(" ","") == str(zip).lower().replace(" ",""):
								returnValue = True
								zip_location = zip_code.zipcode_for
				elif zip_code.zipcode_range.find('-') > -1:
					zipcoderanges_after = zip_code.zipcode_range.split('-')
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
	components = frappe.db.sql('''select name, html from `tabSection Component` order by name''', as_dict=1)
	for item in components:
		item.content = frappe.db.sql('''select group_name, field_label, field_key, field_type, content_type, content, fields_json from `tabSection Content` where parent = %(parent)s and parenttype = "Section Component" order by idx''',{'parent': item.name}, as_dict=1)
	return components

@frappe.whitelist()
def get_styles_list():
	style_groups = frappe.db.sql('''select name from `tabCSS Group` order by name''', as_dict=1)
	for item in style_groups:
		item.style_elements = frappe.db.sql('''select name, property_name, value_type, options_json from `tabCSS Property` where css_group = %(group)s order by name''', {'group': item.name}, as_dict=1)
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
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.api.check_domain')
		
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


def find_web_page_builder_by_route(route_str):
	if not route_str:
		return None
	r = route_str.strip()
	if r.startswith("p/"):
		r = r[2:]
	elif r.startswith("/p/"):
		r = r[3:]
	
	r = r.strip("/")
	
	possible_routes = [
		route_str,
		r,
		"/" + r,
		"p/" + r,
		"/p/" + r
	]
	
	if r == "demo" or r == "":
		possible_routes.extend(["/", "", "demo", "p/demo", "/p/demo"])
		
	for pr in possible_routes:
		res = frappe.db.get_all('Web Page Builder', filters={'route': pr}, fields=['name', 'page_type', 'w_page_type', 'route', 'page_title'])
		if res:
			return res

	# Detail-page fallback: a URL like `shop/product/<id>` has no page of its own.
	# Drop trailing segments and retry so one saved page can serve every record,
	# reading the id from the path. Exact matches above always win, so this only
	# runs for routes that would otherwise 404.
	parts = r.split("/")
	while len(parts) > 1:
		parts = parts[:-1]
		parent = "/".join(parts)
		for pr in (parent, "/" + parent, "p/" + parent, "/p/" + parent):
			res = frappe.db.get_all(
				'Web Page Builder',
				filters={'route': pr},
				fields=['name', 'page_type', 'w_page_type', 'route', 'page_title'],
			)
			if res:
				return res
	return None


@frappe.whitelist(allow_guest=True)
def get_page_content(route=None, user=None, customer=None, domain=None, business=None, application_type="mobile", is_builder=0, start=0, page_length=0):
	page_content = page_type = list_content = list_style = detail_content  = None
	side_menu = sub_header = None
	is_builder = int(is_builder) if is_builder else 0
	start = int(start) if start else 0
	page_length = int(page_length) if page_length else 0

	if user and not customer:
		customer_info = frappe.db.get_all('Customers', filters={'user_id': user})
		if customer_info: customer = customer_info[0].name
		
	check_builder = None
	if business:
		home = frappe.db.get_all('Web Page Builder', filters={'business': business}, fields=['name', 'page_type'])
		if home:
			check_builder = home
			page_content =  get_page_builder_data(home, customer, application_type, business=business, is_builder=is_builder, start=start, page_length=page_length)
			
	if not check_domain("multi_store"):
		business = None
		
	if domain and not route:
		check_website = frappe.db.get_all('Website', filters={'domain_name': domain}, fields=['business', 'theme', 'home_page'])
		if check_website and check_website[0].home_page:
			check_builder = find_web_page_builder_by_route(check_website[0].home_page)
			if check_builder:
				page_content =  get_page_builder_data(check_builder, customer, business=business, is_builder=is_builder, start=start, page_length=page_length)	
				
	if not route and not domain:
		home_page = frappe.db.get_single_value('Website Settings', 'home_page')
		check_builder = find_web_page_builder_by_route(home_page)
		if check_builder:
			page_content =  get_page_builder_data(check_builder, customer, application_type, business=business, is_builder=is_builder, start=start, page_length=page_length)
	elif route:
		if check_domain("saas"):
			business = get_business_from_web_domain(domain)
		check_builder = find_web_page_builder_by_route(route)
		if check_builder:
			page_type = check_builder[0].w_page_type
			if check_builder[0].page_type !="List" and check_builder[0].page_type != "Detail":
				page_content =  get_page_builder_data(check_builder, customer, application_type, business=business, is_builder=is_builder, start=start, page_length=page_length)
		else:
			check_section = frappe.db.get_all('Page Section', filters={'route': route}, fields=['name'])
			if check_section:
				from ecommerce_business_store.cms.doctype.page_section.page_section import get_section_data
				page_content =  get_section_data(check_section[0].name, customer)

	elements = []
	page_resources = []
	page_variables = []
	page_title = None
	# SEO fields for the SPA's <head> (Home.vue updateMetaTags); without them
	# the client could only fall back to page_title.
	seo = {}
	if check_builder:
		try:
			doc = frappe.get_doc("Web Page Builder", check_builder[0].name)
			page_title = doc.page_title or doc.name
			seo = {k: doc.get(k) for k in ("meta_title", "meta_description", "meta_keywords",
			                                "og_title", "og_description", "og_image", "robots")}
			# Project-level tab icon (CMS Project.favicon) so the SPA can swap
			# the favicon per project, including on the Vite dev server where
			# the server-rendered head is not available.
			if doc.get("project") and frappe.db.exists("DocType", "CMS Project"):
				seo["favicon"] = frappe.db.get_value("CMS Project", doc.project, "favicon")
			# Record-level SEO for detail URLs: the same `cms_page_seo` hooks
			# www/frontend.py renders into the server head, run here for the
			# SPA payload — so a client-side navigation to /shop/product/<code>
			# titles the tab and the share tags after the product, not after
			# its template page. `route` is the full requested path; the hook
			# decides whether it applies.
			for hook in frappe.get_hooks("cms_page_seo") or []:
				try:
					extra = frappe.get_attr(hook)(doc, "/" + (route or "").strip("/"))
				except Exception:
					frappe.log_error(frappe.get_traceback(), "cms_page_seo: %s" % hook)
					extra = None
				if not extra:
					continue
				for key in ("meta_title", "meta_description", "meta_keywords", "og_image"):
					if extra.get(key):
						seo[key] = extra[key]
				seo["og_title"] = extra.get("og_title") or extra.get("meta_title") or seo.get("og_title")
				seo["og_description"] = extra.get("og_description") or extra.get("meta_description") or seo.get("og_description")
				break
			# Same rule as get_page_builder_data: is_builder must not hand a guest
			# the draft. This matters more here — the draft's resources/variables
			# describe data sources, not just design. This block swallows
			# exceptions, so gate by selecting the layout rather than throwing.
			if frappe.session.user == "Guest":
				layout_str = doc.layout_json if doc.published else None
			else:
				layout_str = doc.draft_layout_json if (is_builder and doc.draft_layout_json) else doc.layout_json
			if layout_str:
				layout = json.loads(layout_str)
				elements = layout.get('elements', [])
				page_resources = layout.get('resources', []) or []
				page_variables = layout.get('variables', []) or []
		except Exception:
			pass

	if page_type == "List":
		list_content = []
		if check_builder:
			columns = ''
			condition = ''
			order_by = " ORDER BY creation DESC "
			builder_doc = frappe.get_doc('Web Page Builder', check_builder[0].name)
			if builder_doc.condition:
				condition = " WHERE "+builder_doc.condition
			if builder_doc.sort_field:
				order_by = " ORDER BY "+builder_doc.sort_field+" "+ builder_doc.sort_by
			cols_json = json.loads(builder_doc.columns_mapping)
			for x in cols_json:
				for key in x.keys():
					columns += x[key]+" as "+key+","
			columns = columns[:-1]
			list_content = frappe.db.sql(""" SELECT {columns} FROM `tab{document}` doc {condition} {order_by}""".format(condition=condition,order_by=order_by,columns=columns,document=builder_doc.document),as_dict=1)
			list_style = builder_doc.list_style
			if builder_doc.enable_side_menu:
				s_data = None
				if builder_doc.data_fetch_from:
					s_data = frappe.db.get_all(builder_doc.data_fetch_from,fields=['*'])
				side_menu = {"enabled":builder_doc.enable_side_menu,"data":s_data,'position':builder_doc.side_menu_position,'display_field':builder_doc.side_menu_display_field}
			else:
				side_menu = {"enabled":0}

	header_content = None
	footer_content = None
	page_builder_dt = None
	if check_builder:
		theme_settings = frappe.db.get_all("Web Theme",filters={"is_active":1},fields=['default_header','default_footer','enable_page_title','page_title_bg','page_title_tag','title_text_align','page_title_overlay','page_title_color','container_max_width'])
		page_builder_dt = frappe.db.get_all('Web Page Builder', filters={'name': check_builder[0].name}, fields=['text_color','is_transparent_sub_header','sub_header_title','sub_header_bg_color','sub_header_bg_img','footer_component', 'header_component','enable_sub_header','edit_header_style','is_transparent_header','custom_css','owns_design','project'])
		if page_builder_dt:
			if page_builder_dt[0].footer_component:
				footer_content = get_footer_info(page_builder_dt[0].footer_component)
			else:
				if theme_settings:
					if theme_settings[0].default_footer:
						footer_content = get_footer_info(theme_settings[0].default_footer)
			
			if page_builder_dt[0].header_component:
				header_content = get_header_info(page_builder_dt[0].header_component)
			else:
				if theme_settings:
					if theme_settings[0].default_header:
						header_content = get_header_info(theme_settings[0].default_header)

			if page_builder_dt[0].enable_sub_header:
				sub_header = {"enabled":1,"sub_header_title":page_builder_dt[0].sub_header_title,
							  "sub_header_bg_color":page_builder_dt[0].sub_header_bg_color,
							  "is_transparent":page_builder_dt[0].is_transparent_sub_header,
							  "text_color":page_builder_dt[0].text_color,
							  "container_max_width":page_builder_dt[0].container_max_width,
							  "enable_breadcrumbs":page_builder_dt[0].enable_breadcrumbs,
							  "page_title_overlay":page_builder_dt[0].page_title_overlay,
							  "sub_header_bg_img":page_builder_dt[0].sub_header_bg_img,
							  "title_text_align":page_builder_dt[0].title_text_align,
							 }
			else:
				sub_header = {"enabled":0}
				if theme_settings:
					if theme_settings[0].enable_page_title:
						sub_header = {"enabled":1,
							  "sub_header_title":page_builder_dt[0].name,
							  "sub_header_bg_color":theme_settings[0].page_title_bg,
							  "sub_header_bg_img":theme_settings[0].page_title_bg_img,
							  "is_transparent":theme_settings[0].is_transparent,
							  "text_color":theme_settings[0].page_title_color,
							  "page_title_overlay":theme_settings[0].page_title_overlay,
							  "title_text_align":theme_settings[0].title_text_align,
							  "container_max_width":theme_settings[0].container_max_width,
							  "enable_breadcrumbs":theme_settings[0].enable_breadcrumbs,
							 }
			
			if page_builder_dt[0].edit_header_style:
				if page_builder_dt[0].is_transparent_header:
					if header_content:
						header_content.is_transparent_header = 1

	return {
		"sub_header":sub_header,
		"side_menu":side_menu,
		"list_content":list_content,
		"list_style":list_style,
		"page_type":page_type,
		"page_content":page_content,
		"header_content":header_content,
		"footer_content":footer_content,
		"page_id": check_builder[0].name if (check_builder and len(check_builder)>0) else None,
		"page_title": page_title,
		"meta_title": seo.get("meta_title"),
		"meta_description": seo.get("meta_description"),
		"meta_keywords": seo.get("meta_keywords"),
		"og_title": seo.get("og_title"),
		"og_description": seo.get("og_description"),
		"og_image": seo.get("og_image"),
		"robots": seo.get("robots"),
		"favicon": seo.get("favicon"),
		# The page's own stylesheet. It carries the `:root { --tok-*: ... }` block
		# a tokenized page is painted from, so the palette arrives with the page
		# instead of after a second round-trip — no repaint flash. Home.vue has
		# always called applyPageCustomCss(data.custom_css); until now nothing
		# put the field in this payload.
		"custom_css": (page_builder_dt[0].custom_css if page_builder_dt else "") or "",
		# AI-generated pages style every node inline and ship their own CSS, so
		# the site theme's global !important rules must not repaint them. The
		# SPA suppresses that stylesheet on this flag — it was being written by
		# the generator and read by Home.vue, but never carried across in
		# between, so suppression never once fired. int(), because the reader
		# does `!!data.owns_design` and a string "0" is truthy.
		"owns_design": int(page_builder_dt[0].owns_design or 0) if page_builder_dt else 0,
		# Whether the project has opted its website into the site-wide Theme
		# Studio stylesheet + theme colour variables (CMS Project.use_theme_studio).
		# Off, and Home.vue leaves the page to its own custom_css/inline styles
		# exactly as an owns_design page is left. Missing/unknown resolves to on.
		"theme_studio_enabled": theme_studio_enabled_for(page_builder_dt[0].get("project")) if page_builder_dt else 1,
		"builder_type": "Web Page Builder",
		"elements": elements,
		"resources": page_resources,
		"variables": page_variables
	}


@frappe.whitelist(allow_guest=True)
def get_theme_layout():
	"""Lightweight header/footer for the SPA shell.

	The global header/footer composables previously fetched get_page_content
	for a hardcoded page just to read header_content/footer_content, which
	resolved every section of that page server-side. This returns only the
	active theme's default header and footer.
	"""
	header_content = None
	footer_content = None
	theme_settings = frappe.db.get_all("Web Theme", filters={"is_active": 1}, fields=['default_header', 'default_footer'])
	if theme_settings:
		if theme_settings[0].default_header:
			header_content = get_header_info(theme_settings[0].default_header)
		if theme_settings[0].default_footer:
			footer_content = get_footer_info(theme_settings[0].default_footer)
	return {"header_content": header_content, "footer_content": footer_content}


# ── fb2 events/data system: guest-safe data proxy ────────────────────────────
# Published pages define named resources (layout.resources) and repeater
# collections, but guests cannot call frappe.client.get_list. These endpoints
# execute ONLY definitions already stored in the page layout — the stored
# definition is the allowlist. Clients pick the page + name and paginate;
# they can never inject a doctype, filter, or field list.

FB2_BLOCKED_DOCTYPES = {
	"User", "DocType", "DocField", "DocPerm", "Custom Field", "Property Setter",
	"Sessions", "DefaultValue", "Email Account", "Email Queue", "Email Queue Recipient",
	"OAuth Client", "OAuth Bearer Token", "OAuth Authorization Code", "Token Cache",
	"Connected App", "Installed Application", "Scheduled Job Type", "Scheduled Job Log",
	"Error Log", "Activity Log", "Access Log", "Route History", "View Log",
	"System Settings", "Website Settings",
}

# Doctypes where '*' would leak sensitive columns get a fixed safe field list
# instead (Web Page Builder is the default repeater collection, but its layout
# blobs include unpublished draft content).
FB2_DOCTYPE_SAFE_FIELDS = {
	"Web Page Builder": ["name", "page_title", "route", "image", "og_image", "modified", "creation"],
}


def _fb2_load_page_layout(route, is_builder=0):
	check_builder = find_web_page_builder_by_route(route)
	if not check_builder:
		frappe.throw("Page not found", frappe.DoesNotExistError)
	values = frappe.db.get_value(
		"Web Page Builder", check_builder[0].name,
		["published", "layout_json", "draft_layout_json"])
	published, layout_json, draft_layout_json = values or (0, None, None)
	is_builder = int(is_builder) if is_builder else 0
	if is_builder and frappe.session.user != "Guest" and draft_layout_json:
		layout_str = draft_layout_json
	else:
		if not published:
			frappe.throw("Page not published", frappe.PermissionError)
		layout_str = layout_json
	if not layout_str:
		frappe.throw("Page has no layout", frappe.DoesNotExistError)
	try:
		layout = json.loads(layout_str)
	except Exception:
		frappe.throw("Invalid page layout")
	if not isinstance(layout, dict):
		frappe.throw("Invalid page layout")
	return layout


def _fb2_sanitize_fields(fields):
	# '*' is allowed (repeater bindings reference arbitrary record fields);
	# anything that is not a plain column name is dropped.
	if not fields or fields == "*" or "*" in fields:
		return ["*"]
	safe = [f for f in fields if isinstance(f, str) and re.match(r"^[a-zA-Z0-9_]+$", f)]
	return safe or ["name"]


def _fb2_order_by(sort_field, sort_order):
	if not sort_field or not re.match(r"^[a-zA-Z0-9_]+$", str(sort_field)):
		return None
	order = "desc" if str(sort_order or "").lower() == "desc" else "asc"
	return f"`{sort_field}` {order}"


def _fb2_run_doctype_query(doctype, fields, filters, sort_field, sort_order, start, page_length):
	if not doctype or doctype in FB2_BLOCKED_DOCTYPES or not frappe.db.exists("DocType", doctype):
		frappe.throw("This data source is not available", frappe.PermissionError)
	if frappe.get_meta(doctype).issingle:
		frappe.throw("This data source is not available", frappe.PermissionError)
	start = max(int(start or 0), 0)
	page_length = int(page_length or 0) or 20
	page_length = min(max(page_length, 1), 100)
	safe_fields = _fb2_sanitize_fields(fields)
	if safe_fields == ["*"] and doctype in FB2_DOCTYPE_SAFE_FIELDS:
		safe_fields = FB2_DOCTYPE_SAFE_FIELDS[doctype]
	return frappe.get_all(
		doctype,
		fields=safe_fields,
		filters=filters or {},
		order_by=_fb2_order_by(sort_field, sort_order),
		limit_start=start,
		limit_page_length=page_length,
	)


@frappe.whitelist(allow_guest=True)
def run_page_resource(route=None, resource_name=None, start=0, page_length=0, is_builder=0, document_name=None):
	layout = _fb2_load_page_layout(route, is_builder)
	res = None
	for r in layout.get("resources") or []:
		if isinstance(r, dict) and r.get("resource_name") == resource_name:
			res = r
			break
	if not res:
		frappe.throw("Resource not found on this page", frappe.DoesNotExistError)

	rtype = res.get("resource_type")
	if rtype == "Document List":
		limit = int(page_length or 0) or int(res.get("limit") or 20)
		return _fb2_run_doctype_query(
			res.get("document_type"), res.get("fields"), res.get("filters"),
			res.get("sort_field"), res.get("sort_order"), start, limit)

	if rtype == "Document":
		stored_name = res.get("document_name") or ""
		# A client-supplied name is honored only when the author stored a
		# dynamic template (e.g. "{{ route.params.id }}") — the doctype is
		# still fixed by the stored definition.
		docname = document_name if ("{{" in str(stored_name) and document_name) else stored_name
		if not docname or "{{" in str(docname):
			frappe.throw("Document resource has no resolvable document name")
		rows = _fb2_run_doctype_query(
			res.get("document_type"), res.get("fields"), {"name": docname},
			None, None, 0, 1)
		if not rows:
			frappe.throw("Document not found", frappe.DoesNotExistError)
		return rows[0]

	frappe.throw("API resources are called on their own URL, not through this proxy")


def _fb2_find_repeater_settings(layout, node_id):
	def walk(nodes):
		for node in nodes or []:
			if not isinstance(node, dict):
				continue
			if node.get("id") == node_id and node.get("type") == "repeater":
				return node.get("collectionSettings") or {}
			found = walk(node.get("children"))
			if found is not None:
				return found
		return None
	return walk(layout.get("sections"))


@frappe.whitelist(allow_guest=True)
def get_page_repeater_records(route=None, node_id=None, start=0, page_length=0, is_builder=0):
	layout = _fb2_load_page_layout(route, is_builder)
	settings = _fb2_find_repeater_settings(layout, node_id)
	if settings is None:
		frappe.throw("Repeater not found on this page", frappe.DoesNotExistError)
	if (settings.get("source") or "doctype") != "doctype":
		frappe.throw("This repeater uses an external API and is fetched directly")
	limit = int(page_length or 0) or int(settings.get("limit") or 5)
	return _fb2_run_doctype_query(
		settings.get("doctype"), ["*"], settings.get("filters"),
		settings.get("sortBy"), settings.get("sortOrder"), start, limit)


@frappe.whitelist(allow_guest=False)
def get_pages_list(start=0, page_length=24, search=None, status=None, project=None):
	start = int(start)
	page_length = int(page_length)

	filters = []
	or_filters = []

	# Scope to a CMS Project. Filtering here rather than in the client matters
	# because this endpoint is paginated — a client-side filter would only ever
	# narrow the current page. "__unassigned__" mirrors builder2's virtual
	# project for pages that were never linked to one.
	if project:
		if project == '__unassigned__':
			filters.append(['project', 'in', ['', None]])
		else:
			filters.append(['project', '=', project])
	if status == 'Live':
		filters.append(['published', '=', 1])
	elif status == 'Draft':
		filters.append(['published', '=', 0])
	elif status in ('Review', 'Scheduled'):
		# Not a real backing state on this doctype yet — always empty, matching prior client-side behavior.
		filters.append(['name', '=', ''])

	if search:
		or_filters = [
			['page_title', 'like', f'%{search}%'],
			['route', 'like', f'%{search}%'],
		]

	pages = frappe.get_all(
		'Web Page Builder',
		fields=[
			'name', 'page_title', 'route', 'published', 'modified', 'owner',
			'draft_layout_json', 'layout_json', 'project', 'image',
			# SEO metadata — the SEO Manager scores pages on these, so they have to
			# come back with the list rather than being fetched per page.
			'meta_title', 'meta_description', 'meta_keywords',
			'og_title', 'og_description', 'og_image', 'canonical_url',
			'seo_focus_keyphrase',
		],
		filters=filters,
		or_filters=or_filters,
		order_by='modified desc',
		limit_start=start,
		limit_page_length=page_length,
	)
	for p in pages:
		p['preview'] = p.get('image') or p.get('og_image') or ''
		p['page_slug'] = p.get('route')
		p['route'] = p.get('route')
		p['publish_status'] = 'Published' if p.get('published') else 'Draft'
		p['draft_data'] = p.get('draft_layout_json')
		p['published_data'] = p.get('layout_json')
		p['sections_list'] = []
		layout_str = p.get('draft_layout_json') or p.get('layout_json')
		if layout_str:
			try:
				layout = json.loads(layout_str)
				sections = layout.get('sections')
				if not sections and layout.get('elements'):
					elements_list = layout.get('elements', [])
					body_node = None
					for el in elements_list:
						if isinstance(el, dict) and el.get('id') == 'body':
							body_node = el
							break
					if body_node and body_node.get('children'):
						sections = [
							{
								'id': ch.get('id'),
								'name': ch.get('name') or ch.get('type') or 'Section',
								'type': ch.get('thumb') if ch.get('type') == 'section' else (ch.get('type') or 'div'),
								'props': ch.get('styles') or {}
							}
							for ch in body_node.get('children')
						]
				
				if sections:
					p['sections_list'] = [
						{
							'id': s.get('id') or s.get('section') or '',
							'name': s.get('name') or s.get('section_name') or '',
							'type': s.get('type') or s.get('section_type') or '',
							'props': s.get('props') or s.get('style') or {}
						}
						for s in sections
					]
			except Exception:
				pass
	return {'pages': pages, 'has_more': len(pages) == page_length}


@frappe.whitelist(allow_guest=False)
def get_pages_stats():
	total = frappe.db.count('Web Page Builder')
	live = frappe.db.count('Web Page Builder', {'published': 1})
	return {'All': total, 'Live': live, 'Draft': total - live, 'Review': 0, 'Scheduled': 0}


@frappe.whitelist(allow_guest=False)
def get_web_pages_count(doctype='Web Page Builder', search=None, status=None, project=None):
	"""Total rows behind the builder's Pages / Components list.

	The list itself is a paginated `frappe.client.get_list`, so the badge next
	to it cannot be counted client-side — this applies the very same filters
	(see `webPagesListFilters` in FreeBuilder2 / Builder2): `status` Live/Draft
	on `published`, `project` by name or the virtual "unassigned" bucket, and
	the search on the doctype's own title/route (or component) fields.
	Returns {'count': int}."""
	if doctype not in ('Web Page Builder', 'Web Component'):
		doctype = 'Web Page Builder'

	filters = []
	or_filters = []

	if status in ('Live', 'Published'):
		filters.append(['published', '=', 1])
	elif status == 'Draft':
		filters.append(['published', '=', 0])
	elif status in ('Review', 'Scheduled'):
		# No backing state on either doctype yet — mirrors get_pages_list.
		return {'count': 0}

	if project:
		if project in ('unassigned', '__unassigned__'):
			filters.append(['project', 'is', 'not set'])
		else:
			filters.append(['project', '=', project])

	search = (search or '').strip()
	if search:
		like = f'%{search}%'
		if doctype == 'Web Component':
			or_filters = [['title', 'like', like], ['component_name', 'like', like], ['name', 'like', like]]
		else:
			or_filters = [['page_title', 'like', like], ['route', 'like', like]]

	rows = frappe.get_list(
		doctype,
		fields=['count(name) as count'],
		filters=filters,
		or_filters=or_filters,
	)
	return {'count': int(rows[0].get('count') or 0) if rows else 0}


@frappe.whitelist(allow_guest=False)
def save_page_sections(page, sections):
	sections_data = json.loads(sections) if isinstance(sections, str) else sections
	
	if frappe.db.exists('Web Page Builder', page):
		doc = frappe.get_doc('Web Page Builder', page)
		draft_layout = {}
		if doc.draft_layout_json:
			try:
				draft_layout = json.loads(doc.draft_layout_json)
			except Exception:
				pass
		
		if draft_layout and isinstance(draft_layout, dict) and draft_layout.get('elements'):
			elements_list = draft_layout.get('elements', [])
			body_node = None
			for el in elements_list:
				if isinstance(el, dict) and el.get('id') == 'body':
					body_node = el
					break
			
			if body_node:
				current_children = {ch.get('id'): ch for ch in body_node.get('children', []) if isinstance(ch, dict) and ch.get('id')}
				new_children = []
				for s in sections_data:
					if not isinstance(s, dict):
						continue
					sec_id = s.get('id')
					if sec_id in current_children:
						child = current_children[sec_id]
						if s.get('name'):
							child['name'] = s.get('name')
						if s.get('props'):
							child['styles'] = s.get('props')
						new_children.append(child)
					else:
						sec_type = s.get('type') or 'div'
						new_child = {
							'id': sec_id or f"section-{frappe.generate_hash(length=8)}",
							'name': s.get('name') or s.get('type') or 'Section',
							'type': 'section' if sec_type not in ['div', 'text', 'button', 'image'] else sec_type,
							'thumb': sec_type,
							'content': {},
							'styles': s.get('props') or {},
						}
						if new_child['type'] == 'div':
							new_child['children'] = []
						new_children.append(new_child)
				
				body_node['children'] = new_children
				layout_str = json.dumps(draft_layout)
				
				frappe.db.set_value('Web Page Builder', page, {
					'draft_layout_json': layout_str
				})
				frappe.db.commit()
				
				return {
					"status": "Success",
					"sections": sections_data
				}

	layout = {"sections": sections_data}
	layout_str = json.dumps(layout)
	
	if frappe.db.exists('Web Page Builder', page):
		frappe.db.set_value('Web Page Builder', page, {
			'draft_layout_json': layout_str
		})
		frappe.db.commit()
	else:
		doc = frappe.new_doc('Web Page Builder')
		doc.page_title = page
		doc.route = '/' + page.lower().replace(' ', '-')
		doc.published = 0
		doc.draft_layout_json = layout_str
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	
	return {
		"status": "Success",
		"sections": sections_data
	}


@frappe.whitelist(allow_guest=False)
def save_builder_page(page_name, layout_json, page_title=None, page_slug=None):
	if frappe.db.exists('Web Page Builder', page_name):
		doc = frappe.get_doc('Web Page Builder', page_name)
	else:
		doc = frappe.new_doc('Web Page Builder')
		doc.page_title = page_title or page_name
		doc.route = page_slug or ('/' + page_name.lower().replace(' ', '-'))
		doc.published = 0
		
	doc.draft_layout_json = layout_json
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	
	return {"status": "Success", "message": "Page saved successfully"}


@frappe.whitelist(allow_guest=False)
def publish_builder_page(page_name):
	if not frappe.db.exists('Web Page Builder', page_name):
		frappe.throw(f"Web Page Builder {page_name} not found")
		
	doc = frappe.get_doc('Web Page Builder', page_name)
	draft_data = doc.draft_layout_json or '{"sections": []}'
	
	doc.layout_json = draft_data
	doc.published = 1
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "Success", "message": "Page published successfully"}


@frappe.whitelist(allow_guest=False)
def duplicate_page(source_page_id, target_title, target_route):
	if not frappe.db.exists('Web Page Builder', source_page_id):
		frappe.throw(f"Source page {source_page_id} not found")
		
	source_doc = frappe.get_doc('Web Page Builder', source_page_id)
	new_doc = frappe.copy_doc(source_doc)
	new_doc.page_title = target_title
	new_doc.route = target_route
	new_doc.published = 0
	new_doc.layout_json = None
	new_doc.save(ignore_permissions=True)
	frappe.db.commit()
	
	return {
		"status": "success",
		"message": "Page duplicated successfully",
		"new_page_id": new_doc.name
	}


@frappe.whitelist(allow_guest=False)
def update_page_status(page_name, published):
	published = int(published) if published else 0
	if published:
		return publish_builder_page(page_name)
	else:
		if frappe.db.exists('Web Page Builder', page_name):
			frappe.db.set_value('Web Page Builder', page_name, {
				'published': 0,
				'layout_json': None
			})
			frappe.db.commit()
		return {"status": "Success", "message": "Page unpublished successfully"}

@frappe.whitelist(allow_guest=True)
def get_detail_page_content(route):
	check_dt = frappe.db.sql(""" select D.name from `tabDocType` D where D.has_web_view=1 """,as_dict=1)
	for x in check_dt:
		pass

@frappe.whitelist(allow_guest=True)
def get_page_side_menu_data(page_route,linked_doc,page_no=1,page_size=10):
	page_doc = frappe.db.get_all('Web Page Builder',filters={"route":page_route},fields=['columns_mapping','name', 'page_type','document','enable_side_menu','data_fetch_from','condition','sort_field','sort_by'])
	if page_doc:
		if page_doc[0].enable_side_menu == 1 and page_doc[0].data_fetch_from and page_doc[0].document:
			link_fields = frappe.db.sql(""" SELECT fieldname FROM `tabDocField` WHERE parent=%(dt)s AND options=%(linked_doc)s """,{"dt":page_doc[0].document,"linked_doc":page_doc[0].data_fetch_from},as_dict=1)
			if link_fields:
				columns = ''
				condition = ' WHERE doc.{link_field} = "{linked_doc}"'.format(link_field=link_fields[0].fieldname,linked_doc=linked_doc)
				order_by = " ORDER BY creation DESC "
				if page_doc[0].condition:
					condition = " AND "+page_doc[0].condition
				if page_doc[0].sort_field:
					order_by = " ORDER BY "+page_doc[0].sort_field+" "+ page_doc[0].sort_by
				cols_json = json.loads(page_doc[0].columns_mapping)
				for x in cols_json:
					for key in x.keys():
						# frappe.log_error(key,'key')
						columns += x[key]+" as "+key+","
				columns = columns[:-1]
				# frappe.log_error(columns,'columns')
				# frappe.log_error(condition,'condition')
				list_content = frappe.db.sql(""" SELECT {columns} FROM `tab{document}` doc {condition} {order_by} limit {page_no},{page_len} """.format(condition=condition,order_by=order_by,columns=columns,document=page_doc[0].document,page_no = (int(page_no) - 1) * int(page_size),page_len = page_size),as_dict=1)
				return list_content
	return []


def normalize_list_item(item):
	if not item or not isinstance(item, dict):
		return item
	title_val = item.get('list_title') or item.get('title1') or item.get('title') or item.get('label') or ''
	if title_val:
		if not item.get('list_title'): item['list_title'] = title_val
		if not item.get('title1'): item['title1'] = title_val
		if not item.get('title'): item['title'] = title_val
	icon_val = item.get('list_icon') or item.get('icon') or ''
	if icon_val:
		if not item.get('list_icon'): item['list_icon'] = icon_val
		if not item.get('icon'): item['icon'] = icon_val
	desc_val = item.get('list_content') or item.get('subtitle') or item.get('content') or item.get('desc') or item.get('a') or item.get('answer') or ''
	if desc_val:
		if not item.get('list_content'): item['list_content'] = desc_val
		if not item.get('subtitle'): item['subtitle'] = desc_val
		if not item.get('content'): item['content'] = desc_val
		if not item.get('desc'): item['desc'] = desc_val
	q_val = item.get('q') or item.get('question') or ''
	if q_val:
		if not item.get('q'): item['q'] = q_val
		if not item.get('question'): item['question'] = q_val
	a_val = item.get('a') or item.get('answer') or ''
	if a_val:
		if not item.get('a'): item['a'] = a_val
		if not item.get('answer'): item['answer'] = a_val
	return item

def parse_template_content(tmpl):
	mapped_content = {}
	
	custom_data = tmpl.get('custom_section_data')
	if custom_data:
		try:
			parsed = json.loads(custom_data) if isinstance(custom_data, str) else custom_data
			if parsed and isinstance(parsed, dict):
				mapped_content.update(parsed)
		except Exception:
			pass
			
	content_rows = tmpl.get('content')
	if content_rows and isinstance(content_rows, list):
		for row in content_rows:
			field_key = row.get('field_key')
			if field_key:
				val = row.get('content')
				if isinstance(val, str) and (val.strip().startswith('[') or val.strip().startswith('{')):
					try:
						val = json.loads(val)
						if isinstance(val, list):
							val = [normalize_list_item(x) for x in val]
					except Exception:
						pass
				mapped_content[field_key] = val
				if field_key == 'subtitle':
					mapped_content['sub_title'] = val
				if field_key == 'right_image':
					mapped_content['image'] = val
				if field_key == 'image':
					mapped_content['right_image'] = val
					mapped_content['left_image'] = val
				if field_key == 'left_image':
					mapped_content['image'] = val
					
	if not mapped_content.get('_section_name'):
		mapped_content['_section_name'] = tmpl.get('title') or tmpl.get('name') or ''
	if not mapped_content.get('_section_type'):
		mapped_content['_section_type'] = tmpl.get('section_type') or tmpl.get('title') or tmpl.get('name') or ''
	if not mapped_content.get('_template_id'):
		mapped_content['_template_id'] = tmpl.get('name') or ''
		
	return mapped_content


def get_page_builder_data(page, customer=None,application_type="mobile",business=None, is_builder=0, start=0, page_length=0):
	# frappe.log_error(customer, "---customer--page-builder--")
	path = frappe.utils.get_files_path()
	import os
	if page[0].page_type == 'Adaptive':
		ptype =  ('_web')
		if application_type == "mobile":
			ptype =  ('_mobile')
	else:
		ptype = ('_web')
	use_page_builder = 1
	page_builders = frappe.db.get_all("Web Page Builder",filters={"name":page[0].name},fields=['use_page_builder'])

	if page_builders:
		use_page_builder = page_builders[0].use_page_builder
	if use_page_builder:
		is_builder = int(is_builder) if is_builder else 0
		doc = frappe.get_doc("Web Page Builder", page[0].name)
		# get_page_content is allow_guest, so is_builder alone must never unlock a
		# draft: an anonymous caller could otherwise read any page's unreleased
		# edits just by appending is_builder=1. A share token is the only guest
		# route to unpublished content (see get_shared_page_preview); everyone
		# else gets exactly what has been published. Mirrors the guard in
		# _fb2_load_page_layout.
		if frappe.session.user == "Guest":
			if not doc.published:
				frappe.throw("Page not published", frappe.PermissionError)
			layout_str = doc.layout_json
		else:
			layout_str = doc.draft_layout_json if (is_builder and doc.draft_layout_json) else doc.layout_json
		if layout_str:
			try:
				layout = json.loads(layout_str)
				sections_list = [s for s in layout.get('sections', []) if s]
				page_animation = layout.get('pageAnimation')
				# Paginate sections BEFORE resolving them (templates/dynamic data are
				# expensive), so the published page can lazy-load sections on scroll.
				start = int(start) if start else 0
				page_length = int(page_length) if page_length else 0
				if page_length > 0:
					sections_list = sections_list[start:start + page_length]
					if not sections_list:
						# Past the last section — return an empty page instead of
						# falling through to the legacy data_source file path.
						return []
				if sections_list:
					lists = []
					from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
					for sec in sections_list:
						if not sec:
							continue
						
						# Resolve Section Template if templateId is set
						if sec.get('templateId'):
							try:
								tmpl_doc = frappe.get_doc('Section Template', sec.get('templateId'))
								tmpl_data = tmpl_doc.as_dict()
								tmpl_data['content'] = [d.as_dict() for d in tmpl_doc.get('content') or []]
								parsed = parse_template_content(tmpl_data)
								
								if 'content' not in sec or not isinstance(sec['content'], dict):
									sec['content'] = {}
								
								merged_content = parsed.copy()
								merged_content.update(sec['content'])
								sec['content'] = merged_content
								
								sec['thumb'] = tmpl_doc.name
								sec['section_name'] = tmpl_doc.name
								sec['section_type'] = tmpl_doc.name
							except Exception as e:
								frappe.log_error(f"Failed to resolve template {sec.get('templateId')}: {str(e)}", "get_page_builder_data")

						item = {}
						if isinstance(sec.get('content'), dict):
							item.update(sec['content'])
						elif isinstance(sec, dict):
							item.update(sec)
						
						item['section'] = sec.get('id') or sec.get('section')
						item['name'] = sec.get('id') or sec.get('section')
						item['section_name'] = sec.get('name') or sec.get('section_name')
						item['section_type'] = sec.get('type') or sec.get('section_type') or sec.get('name')
						if page_animation and sec.get('type') == 'freebuilder':
							item['_page_animation'] = page_animation
						if sec.get('style') and isinstance(sec['style'], dict):
							item['background_color'] = sec['style'].get('bgColor', '')
							item['style'] = sec.get('style')
						if sec.get('thumb'):
							item['thumb'] = sec.get('thumb')
						if sec.get('image'):
							item['image'] = sec.get('image')
						if sec.get('variant') is not None:
							item['variant'] = sec.get('variant')
						if sec.get('visible') is not None:
							item['visible'] = sec.get('visible')
						
						if item.get('login_required') == 1 and customer:
							try:
								ps_doc = frappe.get_doc('Page Section', item.get('section'))
								item['data'] = get_data_source(ps_doc.query, ps_doc.reference_document, ps_doc.no_of_records, 1, customer)
							except Exception:
								pass
						if item.get('dynamic_data') == 1:
							try:
								if item.get('section_type') in ['Slider','Predefined Section', 'Custom Section', 'Lists', 'Tabs'] or item.get('section'):
									ps_doc = frappe.get_doc('Page Section', item.get('section'))
									ps_doc.business = business
									# Preserve layout options from layout json (e.g. title, subtitle, style updates)
									layout_content = item.copy()
									item = ps_doc.run_method('section_data', customer=customer, add_info=None, store_business=business)
									for k, v in layout_content.items():
										if k not in ['data', 'list_items', 'testimonial_items'] and v is not None:
											item[k] = v
							except Exception:
								pass
						lists.append(item)
					return lists
			except Exception as e:
				frappe.log_error(f"Error parsing layout json: {str(e)}", "get_page_builder_data")

		file_path = os.path.join(path, 'data_source', (page[0].name.lower().replace(' ','_') + ptype + '.json'))
		if not os.path.exists(file_path):
			return []
		with open(file_path) as f:
			data = json.loads(f.read())
			from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
			lists = []
			# frappe.log_error(data, "---page_builders--")
			for item in data:
				# frappe.log_error(item, item.get('section'))
				if item.get('login_required') == 1 and customer:
					doc = frappe.get_doc('Page Section', item.get('section'))
					item['data'] = get_data_source(doc.query, doc.reference_document, doc.no_of_records, 1, customer)
				if item.get('dynamic_data') == 1:
					
					if item['section_type'] in ['Slider','Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
						# frappe.log_error(item.get('section'), "---3--")
						doc = frappe.get_doc('Page Section', item.get('section'))
						doc.business = business
						# Preserve layout options from layout json (e.g. title, subtitle, style updates)
						layout_content = item.copy()
						item = doc.run_method('section_data', customer=customer,add_info=None,store_business=business)
						for k, v in layout_content.items():
							if k not in ['data', 'list_items', 'testimonial_items'] and v is not None:
								item[k] = v

				#updated by boopathy-05.04.2022
				if item.get('section_type')=="Dynamic":
					doc = frappe.get_list('Child Page Section',filters={"page_section":item.get('section')},fields={"name","conditions","page_section","section_type","section_title","reference_document","sort_field","sort_by","custom_section_data","is_editable","dynamic_id","field_list","no_of_records","background_color","text_color"})
					child_section_data = []
					for d in doc:
						sections ={}
						sections['section_title']= d['section_title']
						sections['section_type'] = d['section_type']
						if d['section_type']=="Dynamic Section":
							# frappe.log_error("calling")
							query = "SELECT "
							if not d['field_list']:
								query += "* FROM `tab{reference_document}`"

							if d['field_list'] and d['get_data_from_doctype']==0:
								query += "{field_list} FROM `tab{reference_document}`"

							if d['field_list'] and d['get_data_from_doctype']==1:
								field_list =""
								fields = d['field_list'].split(',')
								for i in fields:
									field_list +="B."+i+","
								l = len(field_list)
								field_list = field_list[:l-1]
								query += "{field_list} FROM `tab{reference_document}` A "
								# frappe.log_error(field_list,"field_list")

							if d['get_data_from_doctype']==1 and d['reference_doc']:
								query += "INNER JOIN `tab{from_doctype}` B ON A.name = B.{reference_field}"

							if d['conditions']:
								query+=" WHERE {conditions}"
							if d['reference_doc'] and d['get_data_from_doctype']==1 and not d['conditions']:
								query += " WHERE A.name='{reference_doc}'"

							if d['reference_doc'] and d['get_data_from_doctype']==1 and d['conditions']:
								query += " and A.name='{reference_doc}'"

							if d['reference_doc'] and d['get_data_from_doctype']==0 and d['conditions']:
								query += "and parent={reference_doc}"

							if d['reference_doc'] and d['get_data_from_doctype']==0 and not d['conditions']:
								query += "WHERE parent={reference_doc}"


							if d['sort_field'] and d['sort_by']:
								query += " ORDER BY {sort_field} {sort_by} "
							if d['no_of_records']:
								query += " LIMIT {no_of_records} "

							if d['get_data_from_doctype']==0:
								res_data = frappe.db.sql(query.format(query=query,field_list=d['field_list'],reference_document=d['reference_document'],conditions=d['conditions'],sort_field=d['sort_field'],sort_by=d['sort_by'],no_of_records=d['no_of_records'],reference_doc=d['reference_doc'],get_data_from_doctype=d['get_data_from_doctype'],from_doctype=d['from_doctype'],reference_field=d['reference_field']),as_dict=1)
							if d['get_data_from_doctype']==1:
								res_data = frappe.db.sql(query.format(query=query,field_list=field_list,reference_document=d['reference_document'],conditions=d['conditions'],sort_field=d['sort_field'],sort_by=d['sort_by'],no_of_records=d['no_of_records'],reference_doc=d['reference_doc'],get_data_from_doctype=d['get_data_from_doctype'],from_doctype=d['from_doctype'],reference_field=d['reference_field']),as_dict=1)
							sections['data'] = res_data
							# frappe.log_error(res_data)
							
						
							#frappe.log_error(custom_section_data,"custom section data")
						child_section_data.append(sections)
					item['child_section_data'] = child_section_data

					#updated by boopathy
				lists.append(item)
			return lists
	else:
		return frappe.db.get_all("Web Page Builder",filters={"name":page[0].name},fields=['content','name','use_page_builder'])

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
	header_list = frappe.db.get_all("Header Component",filters={"name":header_id},fields=['name','is_transparent_header','title','is_menu_full_width','layout_json','enable_top_menu','sticky_on_top','is_dismissable','layout','sticky_header','call_to_action_button','button_text','button_link','link_target','is_transparent_header','sticky_header_background','menu_text_color'])
	if header_list:
		path = frappe.utils.get_files_path()
		if os.path.exists(os.path.join(path, 'data_source', (header_id.lower().replace(' ','_')  + '_web.json'))):
			with open(os.path.join(path, 'data_source', (header_id.lower().replace(' ','_')  + '_web.json'))) as f:
				data = json.loads(f.read())
				from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
				lists = []
				for item in data:
					if item.get('section_type')=="Menu":
						page_section_menu = frappe.get_value("Page Section",item.get('section'),"menu")
						menu = frappe.db.get_all("Menu",filters={"name":page_section_menu},fields=['is_static_menu','name'])
						if menu:
							parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url,is_mega_menu,no_of_column FROM `tabMenus Item` WHERE parent=%(menu_id)s AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":menu[0].name},as_dict=1)
							# parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":menu[0].name},as_dict=1)
							for x in parent_menus:
							 	x.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon,mega_m_col_index FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":x.menu_label,"menu_id":menu[0].name},as_dict=1)
							 	for sub_menu in x.child_menu:
							 		sub_menu.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE parent=%(menu_id)s AND parentfield='menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":sub_menu.menu_label,"menu_id":menu[0].name},as_dict=1)
							item["menus"] = parent_menus
					lists.append(item)
			header_list[0].items = lists
			if header_list[0].enable_top_menu==1:
				left_items =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":header_id},as_dict=1)
				for x in left_items:
					x.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":x.menu_label,"menu_id":header_id},as_dict=1)
					for sub_menu in x.child_menu:
						sub_menu.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Left' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":sub_menu.menu_label,"menu_id":header_id},as_dict=1)
				right_items =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":header_id},as_dict=1)
				for x in right_items:
					x.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":x.menu_label,"menu_id":header_id},as_dict=1)
					for sub_menu in x.child_menu:
						sub_menu.child_menu =  frappe.db.sql(""" SELECT menu_label,redirect_url,icon FROM `tabMenus Item` WHERE position='Right' AND parent=%(menu_id)s AND parentfield='top_menus' AND parent_menu=%(parent_menu)s ORDER BY idx""",{"parent_menu":sub_menu.menu_label,"menu_id":header_id},as_dict=1)
				header_list[0].top_menu = {"left_items":left_items,"right_items":right_items}
		else:
			header_list[0].items = []
			header_list[0].top_menu = {"left_items":[],"right_items":[]}
		return header_list[0]
	return None

def get_footer_info(footer_id):
	footer_list = frappe.db.get_all("Footer Component",filters={"name":footer_id},fields=['name','title','enable_link_icon','layout_json','enable_copyright','copyright_layout','fc_ct_type','cp_fc_alignment','sc_ct_type','cp_sc_alignment','cp_fc_content','cp_sc_content'])
	if footer_list:
		path = frappe.utils.get_files_path()
		file_path = os.path.join(path, 'data_source', (footer_id.lower().replace(' ','_')  + '_web.json'))
		if not os.path.exists(file_path):
			footer_list[0].items = []
			if footer_list[0].layout_json:
				footer_list[0].layout_json_data = json.loads(footer_list[0].layout_json)
			return footer_list[0]
		with open(file_path) as f:
			data = json.loads(f.read())
			from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
			lists = []
			for item in data:
				if item.get('section_type')=="Menu":
					page_section_menu = frappe.get_value("Page Section",item.get('section'),"menu")
					menu = frappe.db.get_all("Menu",filters={"name":page_section_menu},fields=['is_static_menu','name'])
					if menu:
						parent_menus = frappe.db.sql(""" SELECT menu_label,redirect_url FROM `tabMenus Item` WHERE parent=%(menu_id)s AND (parent_menu IS NULL OR parent_menu='') ORDER BY idx""",{"menu_id":menu[0].name},as_dict=1)
						item["menus"] = parent_menus
				lists.append(item)
		# sort INFO data by 'company' key.
		g_list = []
		column_indexes = frappe.db.sql("""SELECT column_index FROM `tabMobile Page Section` WHERE parent=%(f_id)s GROUP BY column_index""",{"f_id":footer_id},as_dict=1)
		for x in column_indexes:
			result = [m for m in lists if m.get("column_index") == x.get("column_index")] 
			# filter(lambda m: m.get("column_index") == x.get("column_index"), lists)
			g_list.append({"column_index":x.column_index,"items":result})
		footer_list[0].items = g_list
		# footer_list[0].g_list = g_list
		if footer_list[0].layout_json:
			footer_list[0].layout_json_data=json.loads(footer_list[0].layout_json)
		return footer_list[0]
	return None

def key_func(k):
    return k['column_index']
 


@frappe.whitelist(allow_guest=True)
def update_website_context(context):
	try:
		if frappe.local.session.data.csrf_token:
			context.csrf_token=frappe.local.session.data.csrf_token
		else:
			context.csrf_token=''
		theme_list = frappe.get_all("Web Theme",filters={"is_active":1},fields=['*'])
		if not theme_list:
			theme_list = frappe.get_all("Web Theme",fields=['*'],order_by='creation desc')
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
			theme_list[0].social_links = frappe.db.get_all("Social Link",filters={"parent":theme_list[0].name},fields=['icon','social_type','link_url'])
			theme_list[0].js_list = frappe.db.get_all("Js List",filters={"parent":theme_list[0].name},fields=['js_file'])
			theme_list[0].css_list = frappe.db.get_all("Css List",filters={"parent":theme_list[0].name},fields=['css_file'])
			context.theme_settings = theme_list[0]
		if default_header:
			if default_header.layout_json:
				default_header.layout_json = json.loads(default_header.layout_json)
		if default_footer:
			if default_footer.layout_json:
				default_footer.layout_json = json.loads(default_footer.layout_json)
		context.header = default_header
		context.footer = default_footer
		context.layout_template = "/templates/Layouts/layout.html"
		context.page_url = get_url()
		if context.doc:
			if context.doc.doctype=="Web Page Builder":
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
						default_header = get_header_info(context.doc.header_component)
						# frappe.log_error(default_header,">>default_header<<")
						if default_header:
							if default_header.layout_json:
								default_header.layout_json = json.loads(default_header.layout_json)
								context.header = default_header
								# frappe.log_error(context.header,">>context.header<<")
					if context.doc.footer_component:
						default_footer = get_footer_info(context.doc.footer_component)
						if default_footer:
							if default_footer.layout_json:
								default_footer.layout_json = json.loads(default_footer.layout_json)
								context.footer = default_footer
				context.p_route = context.doc.route
				if  context.p_route and "/" in context.doc.route:
					context.p_route = context.doc.route.split('/')[1]
				if context.doc.edit_header_style:
					if context.header and context.doc.is_transparent_header:
						context.header.is_transparent_header = 1
		get_device_type(context)
		# frappe.log_error(context.header,">> context.header <<")
		# frappe.log_error(context,">> context data <<")
	except Exception as e:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.api.update_website_context")
	return None

def get_device_type(context):
	try:
		from go1_cms.go1_cms.device_detect.detect import detect_mobile_browser
		from go1_cms.go1_cms.device_detect.utilities import get_user_agent	
		ua=None
		try:
			req = frappe.local.request
			ua = get_user_agent(req)
		except:
			pass
		if ua:
			context.user_agent = ua
			if detect_mobile_browser(ua):
				if "iPad" in ua:
					context.device_type="Desktop"

				else:
					context.device_type="Mobile"
			else:
				context.device_type="Desktop"
		else:
			context.device_type="Desktop"
	except Exception as e:
		context.device_type="Desktop"
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.api.get_device_type") 	
 
@frappe.whitelist(allow_guest=True)
def get_all_website_settings():
	# theme = frappe.get_doc("Theme Settings")
	theme_list = frappe.get_all("Web Theme",filters={"is_active":1},fields=['*'])
	if not theme_list:
		theme_list = frappe.get_all("Web Theme",fields=['*'],order_by='creation desc')

	footer_template = {}
	default_header = default_footer = None
	header_dict = {}
	if theme_list: 
		theme = frappe.get_doc('Web Theme',theme_list[0]['name'])
		if theme.default_header:
			default_header = get_header_info(theme.default_header)
		if theme.default_footer:
			default_footer = get_footer_info(theme.default_footer)

		return {"header_template":default_header,"footer_template":default_footer,"theme_settings":theme}


@frappe.whitelist(allow_guest=True)
def get_testing_footer_template():
	theme = frappe.get_doc("Theme Settings")
	data = get_footer_template(theme.default_footer)
	doc = frappe.get_doc("Footer Component",theme.default_footer)
	footer_list = frappe.get_doc("Footer Component",theme.default_footer)
	source_doc, sections, html = get_source_doc(footer_list,"Desktop")
	add_info = None
	html_list, js_list = get_page_html(doc, sections, html, source_doc, "Desktop", add_info)
	return html_list,js_list



def get_page_html(doc, sections, html, source_doc, device_type, add_info=None, page_no=0, page_len=3):
	#hided by boopathy on 10/08/2022
	# from ecommerce_business_store.ecommerce_business_store.api import get_all_restaurant_data, check_restaurant_distance
	#end
	section_list = sections[int(page_no):int(page_len)]
	data = get_page_section(source_doc)
	html_list = []
	js_list = ''
	res = {}
	#hided by boopathy
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
	#end
	for item in section_list:
		section_html, css, js, reference_document = frappe.db.get_value('Page Section', item.section, [html, 'custom_css', 'custom_js', 'reference_document'])
		if section_html:
			if css:
				if css.find('<style') == -1:
					section_html += '<style>{0}</style>'.format(css)
				else:
					section_html += '{0}'.format(css)
			if js:
				if js.find('<script') == -1:
					if page_no == 0:
						js_list += frappe.render_template('<script>{0}</script>'.format(js), item.as_dict())
					else:
						section_html += '<script>{0}</script>'.format(js)
				else:
					if page_no == 0:
						js_list += frappe.render_template('{0}'.format(js), item.as_dict())
					else:
						section_html += '{0}'.format(js)
		data_source = next((x for x in data if x.get('section') == item.section), None)
		allow = True
		if data_source.get('dynamic_data') == 1:
			if data_source['section_type'] in ['Slider','Predefined Section', 'Custom Section', 'Lists', 'Tabs']:
				pg_doc = frappe.get_doc('Page Section', data_source['section'])
				# data_source = pg_doc.run_method('section_data', {'add_info': add_info})
				data_source = pg_doc.section_data(add_info=add_info)
		if data_source.get('login_required') == 1:
			if frappe.session.user != 'Guest':
				#modified by boopathy on 10/08/22
				# from ecommerce_business_store.cms.doctype.page_section.page_section import get_data_source
				from go1_cms.go1_cms.doctype.page_section.page_section import get_data_source
				#end
				doc = frappe.get_doc('Page Section', item.section)
				data_source['data'] = get_data_source(doc.query, doc.reference_document, doc.no_of_records, 1, business=doc.business)
			else:
				allow = False
		if check_domain('restaurant') and data_source['section_type'] == 'Predefined Section' and doc.is_location_based:
			check_nearby = False
			if data_source.get('check_location'):
				check_nearby = True
			data_source['data'] = get_all_restaurant_data(data_source['data'], distance, check_nearby, latitude, longitude, sid=res.get('sid'), order_type=order_type)
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
			if data_source['section_type'] == 'Custom Section' and data_source['reference_document']=="Product Category":
				category_product_box = frappe.db.get_value("Product Category",data_source['reference_name'],"product_box_for_list_view")
				if category_product_box:
					product_box = category_product_box
			if product_box:
				data_source['product_box'] = frappe.db.get_value('Product Box', product_box, 'route')
			try:
				template = frappe.render_template(section_html, data_source)
				html_list.append({'template': template, 'section': item.section})
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), "ecommerce_business_store.ecommerce_business_store.doctype.web_page_builder.web_page_builder.get_page_html") 
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
		source_doc = 'data_source/{0}_web.json'.format(doc.name.lower().replace(' ', '_'))
	else:
		source_doc = 'data_source/{0}_{1}.json'.format(doc.name.lower().replace(' ', '_'), (view_type if view_type else None))

	return source_doc, sections, html


@frappe.whitelist(allow_guest=True)
def get_blog_list(category=None,page_no=1,page_size=12):
	condition = ""
	if category:
		condition = " AND blog_category = '%s' "%(category)
	bloglist_query = "SELECT name,title,thumbnail_image,blog_intro,published_on,route FROM `tabBlog Post` WHERE published = 1 %s ORDER BY published_on DESC  limit %s,%s"%(condition,(int(page_no) - 1) * int(page_size),page_size)
	return frappe.db.sql(bloglist_query,as_dict=1)


@frappe.whitelist(allow_guest=True)
def get_blog_categories():
	bloglist_query = "SELECT name,title,route FROM `tabBlog Category` WHERE published = 1 ORDER BY creation DESC "
	return frappe.db.sql(bloglist_query,as_dict=1)

@frappe.whitelist(allow_guest=True)
def get_blog_details(route):
	blog_details = frappe.db.get_all("Blog Post",filters={"route":route},fields=["*"])
	if blog_details:
		condition = " AND blog_category = '%s' "%(blog_details[0].blog_category)
		related_bloglist_query = "SELECT name,title,thumbnail_image,blog_intro,published_on,route FROM `tabBlog Post` WHERE published = 1 AND route<>'%s' %s ORDER BY published_on DESC  limit %s,%s"%(route,condition,0,6)
		related_bloglist = frappe.db.sql(related_bloglist_query,as_dict=1)
		comments = frappe.db.get_all("Blog Comments",filters={"blog_name":blog_details[0].name},fields=["name1","email","comments","creation"],order_by="creation desc")
		return {"status":"success","blog_details":blog_details[0],"related_bloglist":related_bloglist,"comments":comments}
	else:
		return {"status":"failed","Message":"Not Found"}


@frappe.whitelist(allow_guest=True)
def insert_blog_comments(data):
	doc = data
	if isinstance(doc, six.string_types):
			doc = json.loads(doc)
	response=doc
	blog=frappe.new_doc('Blog Comments')
	blog.blog_name=response.get('blog')
	blog.name1=response.get('user_name')
	blog.email=response.get('email')
	blog.comments=response.get('message')
	blog.save(ignore_permissions=True)
	return blog.__dict__

@frappe.whitelist()
def get_blogger_bloglist(customer_email):
	check_blogger = frappe.db.get_all("Blogger",filters={"user":customer_email})
	blogger_id = None
	if check_blogger:
		blogger_id = check_blogger[0].name
	return frappe.db.get_all("Blog Post",filters={"blogger":blogger_id},fields=['name','title','blog_category','published_on','route','published','thumbnail_image'])

@frappe.whitelist()
def generate_sections_json():
	sections = []
	secs = frappe.db.get_all("Section Template",order_by="creation ASC",limit_page_length=1000)
	for x in secs:
		s_template = frappe.get_doc("Section Template",x.name)
		st_obj = s_template.as_dict()
		st_obj.creation = None
		st_obj.modified = None
		sections.append(st_obj)
	# frappe.log_error(sections,"sections")

@frappe.whitelist()
def update_web_themes(doc,method):
	frappe.enqueue(update_website_themes, queue='default',doc=doc)
def update_website_themes(doc):
	update_themes = 1
	# if (doc.doctype == "Header Component" or doc.doctype == "Footer Component") and doc.get('update_theme') == 0:
	# 	update_themes = 0
	if update_themes == 1:
		themes = frappe.db.get_all("Web Theme")
		for x in themes:
			theme = frappe.get_doc("Web Theme",x.name)
			theme.save(ignore_permissions=True)
			theme.reload()


"""
Page Builder API - Handle CMS Page Builder operations
"""

import frappe
import json
from frappe.utils import now
from frappe.model.document import Document

@frappe.whitelist()
def get_builder(builder_name):
	"""Get complete builder document"""
	try:
		doc = frappe.get_doc("CMS Page Builder", builder_name)
		frappe.has_permission("CMS Page Builder", "read", doc.name)
		return doc.as_dict()
	except frappe.DoesNotExistError:
		frappe.throw(f"Builder '{builder_name}' not found", frappe.DoesNotExistError)
	except frappe.PermissionError:
		frappe.throw("You don't have permission to access this builder", frappe.PermissionError)

@frappe.whitelist()
def list_builders():
	"""List all available page builders"""
	try:
		builders = frappe.get_list(
			"CMS Page Builder",
			fields=["name", "builder_title", "status", "modified"],
			order_by="modified desc"
		)
		return builders
	except Exception as e:
		frappe.logger().error(f"Error listing builders: {str(e)}")
		frappe.throw("Error fetching builders")

@frappe.whitelist()
def create_builder(builder_name, builder_title, pages=None):
	"""Create a new CMS Page Builder"""
	try:
		doc = frappe.new_doc("CMS Page Builder")
		doc.builder_name = builder_name
		doc.builder_title = builder_title
		doc.status = "Draft"

		# Add initial pages if provided
		if pages and isinstance(pages, str):
			pages = json.loads(pages)

		if pages:
			for page_data in pages:
				doc.append("pages", page_data)

		# If no pages provided, create default Homepage page
		if not pages:
			doc.append("pages", {
				"page_name": "Homepage",
				"page_title": "Home",
				"page_slug": "home",
				"status": "Draft",
				"order": 1
			})

		doc.insert()
		frappe.msgprint(f"Builder '{builder_name}' created successfully")
		return doc.as_dict()
	except frappe.DuplicateEntryError:
		frappe.throw(f"Builder '{builder_name}' already exists")
	except Exception as e:
		frappe.logger().error(f"Error creating builder: {str(e)}")
		frappe.throw(f"Error creating builder: {str(e)}")

@frappe.whitelist()
def update_builder(builder_name, **kwargs):
	"""Update builder properties"""
	try:
		doc = frappe.get_doc("CMS Page Builder", builder_name)

		# Update allowed fields
		allowed_fields = ["builder_title", "status", "project_type", "custom_metadata"]
		for field in allowed_fields:
			if field in kwargs and kwargs[field] is not None:
				doc.set(field, kwargs[field])

		doc.save()
		return doc.as_dict()
	except Exception as e:
		frappe.logger().error(f"Error updating builder: {str(e)}")
		frappe.throw(f"Error updating builder: {str(e)}")

@frappe.whitelist()
def add_page(builder_name, page_data):
	"""Add a new page to builder"""
	try:
		if isinstance(page_data, str):
			page_data = json.loads(page_data)

		doc = frappe.get_doc("CMS Page Builder", builder_name)

		# Auto-increment order
		max_order = max([p.order for p in doc.pages], default=0)
		if "order" not in page_data or not page_data["order"]:
			page_data["order"] = max_order + 1

		doc.append("pages", page_data)
		doc.save()

		return {
			"success": True,
			"page": doc.pages[-1].as_dict(),
			"pages": [p.as_dict() for p in doc.pages]
		}
	except Exception as e:
		frappe.logger().error(f"Error adding page: {str(e)}")
		frappe.throw(f"Error adding page: {str(e)}")

@frappe.whitelist()
def delete_page(builder_name, page_name):
	"""Delete a page from builder"""
	try:
		doc = frappe.get_doc("CMS Page Builder", builder_name)

		# Find and remove the page
		for i, page in enumerate(doc.pages):
			if page.page_name == page_name:
				del doc.pages[i]
				break

		doc.save()
		return {
			"success": True,
			"pages": [p.as_dict() for p in doc.pages]
		}
	except Exception as e:
		frappe.logger().error(f"Error deleting page: {str(e)}")
		frappe.throw(f"Error deleting page: {str(e)}")

@frappe.whitelist()
def reorder_pages(builder_name, page_order):
	"""Reorder pages (page_order is list of page names in new order)"""
	try:
		if isinstance(page_order, str):
			page_order = json.loads(page_order)

		doc = frappe.get_doc("CMS Page Builder", builder_name)

		# Create order map
		order_map = {page_name: order for order, page_name in enumerate(page_order, 1)}

		# Reorder pages
		ordered_pages = []
		for page_name in page_order:
			for page in doc.pages:
				if page.page_name == page_name:
					page.order = order_map[page_name]
					ordered_pages.append(page)
					break

		doc.pages = ordered_pages
		doc.save()

		return {
			"success": True,
			"pages": [p.as_dict() for p in doc.pages]
		}
	except Exception as e:
		frappe.logger().error(f"Error reordering pages: {str(e)}")
		frappe.throw(f"Error reordering pages: {str(e)}")

@frappe.whitelist()
def update_page(builder_name, page_name, **kwargs):
	"""Update page properties"""
	try:
		doc = frappe.get_doc("CMS Page Builder", builder_name)

		# Find page
		page = None
		for p in doc.pages:
			if p.page_name == page_name:
				page = p
				break

		if not page:
			frappe.throw(f"Page '{page_name}' not found")

		# Update allowed fields
		allowed_fields = ["page_title", "page_slug", "status", "custom_metadata"]
		for field in allowed_fields:
			if field in kwargs and kwargs[field] is not None:
				page.set(field, kwargs[field])

		doc.save()
		return page.as_dict()
	except Exception as e:
		frappe.logger().error(f"Error updating page: {str(e)}")
		frappe.throw(f"Error updating page: {str(e)}")

@frappe.whitelist()
def duplicate_page(builder_name, page_name, new_page_name):
	"""Duplicate a page within the same builder"""
	try:
		doc = frappe.get_doc("CMS Page Builder", builder_name)

		# Find source page
		source_page = None
		for p in doc.pages:
			if p.page_name == page_name:
				source_page = p
				break

		if not source_page:
			frappe.throw(f"Page '{page_name}' not found")

		# Create new page data from source
		new_page_data = source_page.as_dict()
		new_page_data.pop("idx", None)
		new_page_data["page_name"] = new_page_name
		new_page_data["page_slug"] = f"{new_page_name.lower().replace(' ', '-')}"

		# Add to builder
		doc.append("pages", new_page_data)
		doc.save()

		return {
			"success": True,
			"page": doc.pages[-1].as_dict(),
			"pages": [p.as_dict() for p in doc.pages]
		}
	except Exception as e:
		frappe.logger().error(f"Error duplicating page: {str(e)}")
		frappe.throw(f"Error duplicating page: {str(e)}")

@frappe.whitelist()
def export_builder(builder_name):
	"""Export builder as JSON"""
	try:
		doc = frappe.get_doc("CMS Page Builder", builder_name)
		export_data = doc.as_dict()

		# Remove system fields
		for field in ["doctype", "docstatus", "creation", "modified_by"]:
			export_data.pop(field, None)

		return {
			"success": True,
			"data": export_data,
			"exported_at": now()
		}
	except Exception as e:
		frappe.logger().error(f"Error exporting builder: {str(e)}")
		frappe.throw(f"Error exporting builder: {str(e)}")

@frappe.whitelist()
def import_builder(builder_name, import_data):
	"""Import builder from JSON"""
	try:
		if isinstance(import_data, str):
			import_data = json.loads(import_data)

		# Check if builder exists
		try:
			doc = frappe.get_doc("CMS Page Builder", builder_name)
			doc.pages = []
		except:
			doc = frappe.new_doc("CMS Page Builder")
			doc.builder_name = builder_name

		# Update fields
		for key, value in import_data.items():
			if key != "pages":
				doc.set(key, value)

		# Import pages
		if "pages" in import_data:
			doc.pages = []
			for page_data in import_data["pages"]:
				page_data.pop("idx", None)
				doc.append("pages", page_data)

		doc.save()
		return {
			"success": True,
			"doc": doc.as_dict()
		}
	except Exception as e:
		frappe.logger().error(f"Error importing builder: {str(e)}")
		frappe.throw(f"Error importing builder: {str(e)}")

@frappe.whitelist()
def publish_page_builder(page_name):
	"""
	Promotes the draft layout to the live layout and updates public web assets.
	"""
	allowed_roles = {'System Manager', 'Administrator', 'CMS Admin'}
	user_roles = set(frappe.get_roles(frappe.session.user))
	if not (user_roles & allowed_roles):
		frappe.throw('Not permitted to publish pages', frappe.PermissionError)

	doc = frappe.get_doc("Web Page Builder", page_name)
	
	if not doc.draft_layout_json:
		frappe.throw("No draft layout found to publish")

	# Promote draft to live layout
	doc.layout_json = doc.draft_layout_json
	doc.published = 1
	
	# Save triggers construct_html() to rewrite data_source/{page_name}_web.json
	doc.save(ignore_permissions=True)

	from go1_cms.go1_cms.doctype.web_page_publish_log.web_page_publish_log import record_publish
	record_publish(doc, source="Page")

	frappe.db.commit()

	return {"status": "success", "message": "Page published to production successfully"}

@frappe.whitelist()
def publish_project(project_name, page_names=None):
	"""
	Publishes all or selected Web Page Builder pages belonging to the project
	and updates the Project status to 'Published'.
	"""
	allowed_roles = {'System Manager', 'Administrator', 'CMS Admin'}
	user_roles = set(frappe.get_roles(frappe.session.user))
	if not (user_roles & allowed_roles):
		frappe.throw('Not permitted to publish projects', frappe.PermissionError)

	project = frappe.get_doc("CMS Project", project_name)

	# Parse page_names if passed as JSON string
	if isinstance(page_names, str):
		import json
		try:
			page_names = json.loads(page_names)
		except Exception:
			pass

	# Build filters
	filters = {"project": project_name}
	if page_names:
		filters["name"] = ["in", page_names]

	pages = frappe.get_all("Web Page Builder", filters=filters, fields=["name"])

	from go1_cms.go1_cms.doctype.web_page_publish_log.web_page_publish_log import record_publish

	published_count = 0
	for page in pages:
		pdoc = frappe.get_doc("Web Page Builder", page.name)
		if pdoc.draft_layout_json:
			pdoc.layout_json = pdoc.draft_layout_json
		pdoc.published = 1
		pdoc.save(ignore_permissions=True)
		record_publish(pdoc, source="Project")
		published_count += 1

	project.status = "Published"
	project.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"status": "success",
		"message": f"Project and {published_count} pages published to production successfully."
	}


@frappe.whitelist()
def create_static_section(project_id, section_name, cms_v4_enabled=False, field_data=None):
	"""
	Create a new static section template with optional cms_v4 support.
	"""
	try:
		doc = frappe.get_doc({
			"doctype": "Section Template",
			"title": section_name,
			"section_type": "Static Section",
			"cms_v4_enabled": cms_v4_enabled,
			"device_type": "Web & Mobile"
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"status": "success",
			"message": f"Static section '{section_name}' created successfully.",
			"section_id": doc.name,
			"cms_v4_enabled": cms_v4_enabled
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "create_static_section")
		return {
			"status": "error",
			"message": str(e)
		}


@frappe.whitelist()
def get_section_templates_for_project(project_id=None, cms_v4_only=False):
	"""
	Get all section templates, optionally filtered by project or cms_v4 support.
	"""
	try:
		filters = {}
		if cms_v4_only:
			filters["cms_v4_enabled"] = 1

		templates = frappe.get_all(
			"Section Template",
			filters=filters,
			fields=[
				"name",
				"title",
				"section_type",
				"section_group",
				"device_type",
				"cms_v4_enabled",
				"image",
				"modified"
			],
			order_by="modified desc"
		)

		return {
			"status": "success",
			"templates": templates,
			"total": len(templates)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "get_section_templates_for_project")
		return {
			"status": "error",
			"message": str(e),
			"templates": []
		}


@frappe.whitelist()
def update_section_template_cms_v4(section_template_name, cms_v4_enabled=False):
	"""
	Update cms_v4 flag for a section template.
	"""
	try:
		doc = frappe.get_doc("Section Template", section_template_name)
		doc.cms_v4_enabled = cms_v4_enabled
		doc.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"status": "success",
			"message": f"Section template updated with cms_v4_enabled={cms_v4_enabled}",
			"cms_v4_enabled": cms_v4_enabled
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "update_section_template_cms_v4")
		return {
			"status": "error",
			"message": str(e)
		}


# ─────────────────────────────────────────────────────────────────────────────
# GO1CMS Web Clipper — Chrome Extension API
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def import_section_from_extension(section_name, section_html, category="General",
                                  thumbnail_base64="", source_url=""):
	"""
	Receives a section captured by the GO1CMS Web Clipper Chrome extension
	and saves it as a reusable 'Clipped Section' in GO1CMS.

	Args:
		section_name    (str): Human-readable name for the section.
		section_html    (str): The captured HTML (with inlined computed styles).
		category        (str): Section category (Hero, Navbar, Footer, etc.)
		thumbnail_base64(str): Base64-encoded JPEG screenshot of the section.
		source_url      (str): The URL of the page this section was clipped from.

	Returns:
		dict: { status, name, message }
	"""
	try:
		if not section_name or not section_html:
			frappe.throw("section_name and section_html are required.")

		# Sanitise name for use as docname
		safe_name = section_name.strip()[:80]

		# Save thumbnail to file if provided
		thumbnail_url = ""
		if thumbnail_base64 and thumbnail_base64.startswith("data:image"):
			try:
				import base64
				header, encoded = thumbnail_base64.split(",", 1)
				file_data = base64.b64decode(encoded)
				file_name = frappe.scrub(safe_name) + "_clipper_thumb.jpg"
				file_doc = frappe.get_doc({
					"doctype": "File",
					"file_name": file_name,
					"content": file_data,
					"is_private": 0,
					"decode": False,
				})
				file_doc.insert(ignore_permissions=True)
				thumbnail_url = file_doc.file_url
			except Exception:
				frappe.log_error(frappe.get_traceback(), "go1cms_clipper.save_thumbnail")

		# Check if a doctype called 'Clipped Section' exists (custom doctype we create)
		# If not, fall back to saving as a Page Section or just a custom record
		if frappe.db.exists("DocType", "Clipped Section"):
			doc = frappe.get_doc({
				"doctype": "Clipped Section",
				"section_name": safe_name,
				"section_html": section_html,
				"category": category,
				"thumbnail": thumbnail_url,
				"source_url": source_url,
				"clipped_by": frappe.session.user,
				"clipped_on": frappe.utils.now(),
			})
			doc.insert(ignore_permissions=True)
			frappe.db.commit()
			return {"status": "ok", "name": doc.name, "message": "Section imported successfully."}

		else:
			# Fallback: store in a simple JSON file or frappe cache
			# Save as a predefined section entry in go1_cms custom storage
			existing = frappe.cache().get_value("go1cms_clipped_sections") or []
			import uuid
			entry = {
				"id": str(uuid.uuid4()),
				"name": safe_name,
				"html": section_html,
				"category": category,
				"thumbnail": thumbnail_url,
				"source_url": source_url,
				"clipped_by": frappe.session.user,
				"clipped_on": frappe.utils.now(),
			}
			existing.append(entry)
			frappe.cache().set_value("go1cms_clipped_sections", existing)
			return {"status": "ok", "name": entry["id"], "message": "Section imported to cache."}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "go1cms.import_section_from_extension")
		return {"status": "error", "error": str(e), "message": "Import failed."}


@frappe.whitelist()
def get_imported_sections(category=None):
	"""
	Returns all sections imported via the GO1CMS Web Clipper.
	Used by the builder sidebar to show clipped sections.

	Args:
		category (str, optional): Filter by category.

	Returns:
		list: List of clipped section dicts.
	"""
	try:
		if frappe.db.exists("DocType", "Clipped Section"):
			filters = {}
			if category:
				filters["category"] = category
			sections = frappe.get_all(
				"Clipped Section",
				filters=filters,
				fields=["name", "section_name", "category", "thumbnail", "source_url",
				        "section_html", "clipped_by", "clipped_on"],
				order_by="clipped_on desc",
				limit=100,
			)
			return {"status": "ok", "sections": sections}
		else:
			# Read from cache fallback
			all_sections = frappe.cache().get_value("go1cms_clipped_sections") or []
			if category:
				all_sections = [s for s in all_sections if s.get("category") == category]
			return {"status": "ok", "sections": all_sections}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "go1cms.get_imported_sections")
		return {"status": "error", "error": str(e), "sections": []}


@frappe.whitelist()
def save_clipped_section_to_page(page_route, section_html, section_name="Clipped Section"):
	"""
	Attaches a clipped section (raw HTML from Web Clipper) to a Web Page Builder page
	as a new page section, so it appears in the builder canvas.

	Args:
		page_route   (str): The route of the Web Page Builder page.
		section_html (str): The captured HTML string.
		section_name (str): Display name for the section.

	Returns:
		dict: { page_section } — the new section ID for the builder to render.
	"""
	try:
		import uuid

		page_builder = frappe.get_doc('Web Page Builder', {"route": page_route})
		new_section_id = "clipped_" + str(uuid.uuid4()).replace("-", "")[:12]

		# Build a minimal layout_json for the clipped section
		layout_json = [{
			"u_id": new_section_id + "_row",
			"type": "row",
			"columns": [{
				"u_id": new_section_id + "_col",
				"bs_width": "col-md-12",
				"rows": [],
				"components": [{
					"component_title": "Custom HTML",
					"cid": new_section_id + "_cmp",
					"custom_html": section_html,
				}]
			}]
		}]

		# Append as a Web Section child record
		page_builder.append("web_section", {
			"section": None,
			"section_title": section_name,
			"layout_type": "Clipped Section",
			"page_section": new_section_id,
			"layout_json": frappe.as_json(layout_json),
			"clipped_html": section_html,
		})

		page_builder.save(ignore_permissions=True)
		frappe.db.commit()

		return {"status": "ok", "page_section": new_section_id}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "go1cms.save_clipped_section_to_page")
		return {"status": "error", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# Page share links — a view-only external preview URL for one page
# ═══════════════════════════════════════════════════════════════════════════════

SHARE_ALLOWED_ROLES = {'System Manager', 'Administrator', 'CMS Admin'}


def _share_guard(page):
	"""Only page editors may create, read, rotate or send a share link."""
	user_roles = set(frappe.get_roles(frappe.session.user))
	if not (user_roles & SHARE_ALLOWED_ROLES):
		frappe.throw('Not permitted to share pages', frappe.PermissionError)
	if not frappe.db.exists('Web Page Builder', page):
		frappe.throw('Page not found', frappe.DoesNotExistError)


def _get_share_doc(page, create=False):
	name = frappe.db.get_value('Web Page Share', {'page': page})
	if name:
		return frappe.get_doc('Web Page Share', name)
	if not create:
		return None
	doc = frappe.get_doc({
		'doctype': 'Web Page Share',
		'page': page,
		'enabled': 0,
		'invites': '[]',
	})
	doc.insert(ignore_permissions=True)
	return doc


def _share_base_url():
	"""Public base for share links — the configured CMS domain wins, exactly as
	the Desk 'Preview' button resolves public URLs."""
	here = (get_url() or '').rstrip('/')
	# While working locally, a link to the production domain would 404 — that
	# site has neither this token nor the draft. Keep local links local.
	if 'localhost' in here or '127.0.0.1' in here:
		return here
	try:
		settings = frappe.get_cached_doc('CMS Settings', 'CMS Settings')
		if settings and int(settings.get('use_other_domain') or 0) and settings.get('domain'):
			return settings.get('domain').rstrip('/')
	except Exception:
		pass
	return here


def _share_payload(doc):
	try:
		invites = json.loads(doc.invites or '[]')
	except Exception:
		invites = []
	try:
		layout = json.loads(doc.layout or '{}')
	except Exception:
		layout = {}
	return {
		'page': doc.page,
		'token': doc.token,
		'enabled': int(doc.enabled or 0),
		# The link is only handed out while sharing is on.
		'url': '{}/preview/{}'.format(_share_base_url(), doc.token) if doc.enabled else '',
		'invites': invites,
		'layout': layout,
	}


def _store_layout(doc, layout):
	"""The owner's canvas arrangement travels with the link so the shared
	preview renders exactly what the builder's preview mode shows."""
	if layout in (None, ''):
		return False
	if isinstance(layout, six.string_types):
		try:
			layout = json.loads(layout)
		except Exception:
			return False
	if not isinstance(layout, dict):
		return False
	doc.layout = json.dumps(layout)
	return True


@frappe.whitelist()
def get_page_share_link(page, layout=None):
	"""Current share state for a page (creates a dormant, disabled link row).
	Any canvas layout passed in is stored, keeping the shared view in step with
	the builder canvas the owner is looking at."""
	_share_guard(page)
	doc = _get_share_doc(page, create=True)
	if _store_layout(doc, layout):
		doc.save(ignore_permissions=True)
		frappe.db.commit()
	return _share_payload(doc)


@frappe.whitelist()
def set_page_share_link(page, enabled=1, regenerate=0, layout=None):
	"""Turn link sharing on/off, optionally rotating the token."""
	from frappe.utils import random_string

	_share_guard(page)
	doc = _get_share_doc(page, create=True)
	doc.enabled = 1 if int(enabled or 0) else 0
	_store_layout(doc, layout)
	if int(regenerate or 0) or not doc.token:
		doc.token = random_string(32)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return _share_payload(doc)


@frappe.whitelist()
def invite_to_page_share(page, emails, message=None):
	"""Email the view-only preview link to one or more people."""
	_share_guard(page)
	try:
		recipients = json.loads(emails) if isinstance(emails, six.string_types) else (emails or [])
	except Exception:
		recipients = [e.strip() for e in (emails or '').split(',')]
	recipients = [e.strip() for e in recipients if e and e.strip()]
	if not recipients:
		frappe.throw('No email address given')

	doc = _get_share_doc(page, create=True)
	if not doc.enabled:
		doc.enabled = 1
		doc.save(ignore_permissions=True)

	payload = _share_payload(doc)
	url = payload['url']
	page_title = frappe.db.get_value('Web Page Builder', page, 'page_title') or page
	sender_name = frappe.db.get_value('User', frappe.session.user, 'full_name') or frappe.session.user

	body = """
		<p>{sender} shared a preview of <b>{title}</b> with you.</p>
		{note}
		<p><a href="{url}" style="display:inline-block;background:#1b6bf9;color:#fff;
			padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:600;">Open preview</a></p>
		<p style="color:#6b7280;font-size:12px;">This is a view-only link — the page cannot be edited from it.<br>{url}</p>
	""".format(
		sender=frappe.utils.escape_html(sender_name),
		title=frappe.utils.escape_html(page_title),
		note='<p>{}</p>'.format(frappe.utils.escape_html(message)) if message else '',
		url=url,
	)

	sent, failed = [], []
	for email in recipients:
		try:
			frappe.sendmail(
				recipients=[email],
				subject='{} shared a preview: {}'.format(sender_name, page_title),
				message=body,
				reference_doctype='Web Page Share',
				reference_name=doc.name,
			)
			sent.append(email)
		except Exception:
			# No outgoing email account (common on dev sites) — keep the invite
			# recorded so the link can still be copied out by hand.
			frappe.log_error(frappe.get_traceback(), 'go1cms.invite_to_page_share')
			failed.append(email)

	try:
		invites = json.loads(doc.invites or '[]')
	except Exception:
		invites = []
	known = {i.get('email') for i in invites}
	for email in recipients:
		if email not in known:
			invites.append({'email': email, 'invited_on': now(), 'invited_by': frappe.session.user})
	doc.invites = json.dumps(invites)
	doc.save(ignore_permissions=True)
	frappe.db.commit()

	result = _share_payload(doc)
	result.update({'sent': sent, 'failed': failed})
	return result


def _shared_page_payload(row):
	raw = row.get('draft_layout_json') or row.get('layout_json')
	layout = {}
	if raw:
		try:
			layout = json.loads(raw) if isinstance(raw, six.string_types) else raw
		except Exception:
			layout = {}
	return {
		'id': row.get('name'),
		'title': row.get('page_title') or row.get('name'),
		'route': row.get('route') or '',
		'custom_css': row.get('custom_css') or '',
		'page_animation': layout.get('pageAnimation'),
		'sections': layout.get('sections') or [],
	}


@frappe.whitelist(allow_guest=True)
def get_shared_page_preview(token):
	"""Read-only payload behind a share token: the shared page plus the rest of
	its project, so the preview is a navigable site. The ONLY guest entry point
	for draft layouts — the token is the capability, nothing else is exposed.

	A page with no project shares only itself; it must never drag every other
	unassigned draft on the site into a public link."""
	if not token:
		frappe.throw('Preview link not found', frappe.DoesNotExistError)

	share = frappe.db.get_value(
		'Web Page Share', {'token': token, 'enabled': 1}, ['name', 'page', 'layout'], as_dict=True)
	if not share:
		frappe.throw('This preview link is no longer available', frappe.PermissionError)
	try:
		layout = json.loads(share.get('layout') or '{}')
	except Exception:
		layout = {}

	fields = ['name', 'page_title', 'route', 'custom_css', 'project', 'draft_layout_json', 'layout_json']
	entry = frappe.db.get_value('Web Page Builder', share.page, fields, as_dict=True)
	if not entry:
		frappe.throw('Page not found', frappe.DoesNotExistError)

	project_label = ''
	if entry.get('project'):
		project_label = frappe.db.get_value('CMS Project', entry.get('project'), 'project_name') or entry.get('project')

	# The canvas the owner shared defines the page set: the frames they had laid
	# out. Falling back to the project, then to the page on its own — a page with
	# no project and no captured canvas must never drag other drafts along.
	wanted = [k for k in (layout.get('positions') or {}).keys()]
	rows = []
	if wanted:
		rows = frappe.get_all(
			'Web Page Builder', filters={'name': ['in', wanted]},
			fields=fields, order_by='creation asc', limit_page_length=0) or []
	if not rows and entry.get('project'):
		rows = frappe.get_all(
			'Web Page Builder', filters={'project': entry.get('project')},
			fields=fields, order_by='creation asc', limit_page_length=0) or []
	if not rows:
		rows = [entry]
	if not any(r.get('name') == share.page for r in rows):
		rows.insert(0, entry)

	pages = [_shared_page_payload(r) for r in rows]
	# the shared page always opens first
	pages.sort(key=lambda p: 0 if p['id'] == share.page else 1)

	return {
		'project': project_label,
		'entry': share.page,
		'page_title': entry.get('page_title') or share.page,
		'pages': pages,
		'layout': layout,
		'view_only': True,
	}
