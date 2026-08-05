# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt
import frappe
import json
import os
import re
from frappe.utils import get_files_path
from frappe.model.document import Document

# The fence delimiting the Theme Studio generated block inside page_css. Declared
# here because this doctype owns page_css; cms_frontend.design_tokens is the
# writer and imports it rather than keeping a second copy — one regex, so a
# marker change can never leave the writer appending blocks instead of replacing
# them. Must stay in step with the emitter in design_tokens._studio_css_block.
THEME_STUDIO_CSS_RE = re.compile(
	r"/\*\s*---\s*Theme Studio Generated Start\s*---\s*\*/"
	r"[\s\S]*?"
	r"/\*\s*---\s*Theme Studio Generated End\s*---\s*\*/"
)


class WebTheme(Document):
	def validate(self):
		try:
			if self.is_active==1:
				existing_list = frappe.db.sql('''UPDATE `tabWeb Theme` SET is_active=0 WHERE name!="{theme_name}"'''.format(theme_name=self.name))
				frappe.db.commit()
		except Exception as e:
			frappe.log_error(frappe.get_traceback(),"validate web theme")

	def on_update(self):
		try:
			path, sitename = get_path_name()
			if path:
				# By gopi 3/9/22
				generate_webtheme_css_file(path,sitename,self)
		except Exception as e:
			frappe.log_error(frappe.get_traceback(),"theme")
			

@frappe.whitelist()
def minify_string(html):
	import re
	# return_String =  htmlmin.minify(html.replace('\n',''),pre_tags=(u'pre', u'textarea', u'style',u'script'),remove_comments=True,remove_all_empty_space=True,remove_optional_attribute_quotes=False)
	return_String = html.replace('\n','')
	return re.sub(">\s*<","><",return_String)


@frappe.whitelist()
def get_path_name():
	path = sitename = None
	# frappe.log_error(frappe.get_installed_apps(),">> installed apps <<")
	if "go1_cms" in frappe.get_installed_apps():
		path = frappe.get_app_path("go1_cms")
		# frappe.log_error(path,">> path <<")
		sitename = 'go1_cms'
	return path, sitename


def generate_webtheme_css_file(path,sitename,self):
	try:
		is_custom_header = 0
		doc_obj = self
		# assign the global fonts properties
		doc_obj.primary_font_family = ""
		doc_obj.primary_font_weight = ""
		doc_obj.secondary_font_family = ""
		doc_obj.secondary_font_weight =""
		doc_obj.text_font_family =""
		doc_obj.text_font_weight =""
		doc_obj.accent_font_family=""
		doc_obj.accent_font_weight=""
		if self.global_fonts:
			for fonts in self.global_fonts:
				if fonts.title and fonts.title == "Primary":
					doc_obj.primary_font_family = fonts.font_family_name if fonts.font_family_name else ""
					doc_obj.primary_font_weight = fonts.font_weight if fonts.font_weight else ""
				elif fonts.title and fonts.title == "Secondary":
					doc_obj.secondary_font_family = fonts.font_family_name if fonts.font_family_name else ""
					doc_obj.secondary_font_weight = fonts.font_weight if fonts.font_weight else ""
				elif fonts.title and fonts.title == "Text":
					doc_obj.text_font_family = fonts.font_family_name if fonts.font_family_name else ""
					doc_obj.text_font_weight = fonts.font_weight if fonts.font_weight else ""
				elif fonts.title and fonts.title == "Accent":
					doc_obj.accent_font_family = fonts.font_family_name if fonts.font_family_name else ""
					doc_obj.accent_font_weight = fonts.font_weight if fonts.font_weight else ""
		# end
		# check and append custom css
		doc_obj.page_css = (self.page_css.replace('\n','')) if self.page_css else ""
		# check and read css file
		# css_file_data=""
		
		# end
		# Check and assign vaiable css 
		var_name_css = ""
		if doc_obj.heading and len(doc_obj.heading) > 0: 
			for var in doc_obj.heading:
				if var.css_design:
					# frappe.log_error(var.name1,">>tag name<<")
					g_fonts = replace_value_of_globalfonts(var.css_design,doc_obj)
					if g_fonts:
						var_name_css += g_fonts
					# var_name_css += json.loads(var.css_design)
		if doc_obj.text and len(doc_obj.text) > 0: 
			for var in doc_obj.text:
				if var.css_design:
					# frappe.log_error(var.name1,">>tag name<<")
					global_fonts = replace_value_of_globalfonts(var.css_design,doc_obj)
					if global_fonts:
						var_name_css += global_fonts
					# var_name_css += json.loads(var.css_design)
		doc_obj.var_name_css = var_name_css
		# end
		# check and assign buttons property
		btn_css = ""
		if doc_obj.buttons_table and len(doc_obj.buttons_table) > 0:
			for btn in doc_obj.buttons_table:
				if btn.css_design:
					# frappe.log_error(btn.name1,">>tag name<<")
					if replace_value_of_globalfonts(btn.css_design,doc_obj):
						btn_css += replace_value_of_globalfonts(btn.css_design,doc_obj)
					# btn_css += json.loads(btn.css_design)
		doc_obj.btn_var_name_css = btn_css
		# frappe.log_error(doc_obj.btn_var_name_css,"btn_var_name_css")
		# end
		# render the css template
		template = frappe.get_template("templates/includes/web_themes.css")
		global_header_css = None
		if doc_obj.default_header:
			doc_obj.header_settings = frappe.get_doc("Header Component",doc_obj.default_header)
			# frappe.log_error(doc_obj.header_settings.as_dict(),">> doc_obj.header_settings <<")
			""" for map font family """
			if doc_obj.header_settings.font_family:
				doc_obj.header_settings.font_family = frappe.db.get_value("CSS Font",doc_obj.header_settings.font_family,"font_family")
			if doc_obj.header_settings.m_font_family:
				doc_obj.header_settings.m_font_family = frappe.db.get_value("CSS Font",doc_obj.header_settings.m_font_family,"font_family")
			""" End """
			header_template = frappe.get_template("templates/includes/header.css")
			header_css = header_template.render({'header_settings':doc_obj.header_settings})
			global_header_css = header_css
			is_custom_header = 1
		if doc_obj.default_footer:
			doc_obj.footer_css = frappe.get_doc("Footer Component",doc_obj.default_footer)
			""" for map font family """
			if doc_obj.footer_css.font_family:
				doc_obj.footer_css.font_family = frappe.db.get_value("CSS Font",doc_obj.footer_css.font_family,"font_family")
			if doc_obj.footer_css.f_txt_font_family:
				doc_obj.footer_css.f_txt_font_family = frappe.db.get_value("CSS Font",doc_obj.footer_css.f_txt_font_family,"font_family")
			# frappe.log_error(doc_obj.footer_css.as_dict(),'doc_obj.footer_css')
			# frappe.log_error(doc_obj.footer_css.f_txt_font_family,'doc_obj.footer_css.f_txt_font_family')
			""" End """
		font_list = []
		css_fonts = frappe.db.get_all("CSS Font",fields=['font_name','font_type','font_url','font_family'])
		for x in css_fonts:
			if x.font_type == "Google":
				font_list.append({"font_family_url":x.font_url})
		doc_obj.font_list = font_list
		webtheme_css = template.render({'doc':doc_obj})
		if global_header_css:
			webtheme_css += global_header_css
		css_file_name = self.name.lower().replace(' ', '-')+".css"
		path = get_files_path()
		pages = frappe.db.get_all("Web Page Builder",filters={"published":1},fields=['route','name','header_component','footer_component','edit_header_style','is_transparent_header','menu_text_color','menu_hover_bg','menu_hover_text_color'])
		header_settings = None
		for page in pages:
			web_sections = frappe.db.sql("""SELECT P.class_name,P.css_text,P.name FROM `tabMobile Page Section` M INNER JOIN `tabPage Section` P ON M.section=P.name WHERE M.parent = %(page_name)s""",{"page_name":page.name},as_dict=1)
			for x in web_sections:
				header_settings = None
				if page.header_component:
					template = frappe.get_template("templates/includes/header.css")
					header_settings = frappe.get_doc("Header Component",page.header_component)
					""" for map font family """
					if header_settings.font_family:
						header_settings.font_family = frappe.db.get_value("CSS Font",header_settings.font_family,"font_family")
					if header_settings.m_font_family:
						header_settings.m_font_family = frappe.db.get_value("CSS Font",header_settings.m_font_family,"font_family")
					""" End """
					p_route = page.route
					if "/" in p_route:
						p_route = p_route.split('/')[1]
					# frappe.log_error(header_settings.as_dict(),"<< header_settings >>")
					# frappe.log_error(p_route,"<< p_route >>")
					header_css = template.render({'header_settings':header_settings,"page_route":p_route})
					# frappe.log_error(header_css,"<< header_css >>")
					webtheme_css+=header_css
				if page.footer_component:
					p_route = page.route
					if "/" in p_route:
						p_route = p_route.split('/')[1]
					template = frappe.get_template("templates/includes/footer.css")
					footer_settings = frappe.get_doc("Footer Component",page.footer_component)
					""" for map font family """
					if footer_settings.font_family:
						footer_settings.font_family = frappe.db.get_value("CSS Font",footer_settings.font_family,"font_family")
					if footer_settings.f_txt_font_family:
						footer_settings.f_txt_font_family = frappe.db.get_value("CSS Font",footer_settings.f_txt_font_family,"font_family")
					""" End """
					footer_css = template.render({'footer_settings':footer_settings,"page_route":p_route})
					webtheme_css+=footer_css

				if x.css_text:
					webtheme_css+=x.css_text
				section_content = frappe.db.get_all("Section Content",filters={"parent":x.name},fields=['css_text'])
				sec_columns = frappe.db.get_all("Section Column CSS",filters={"parent":x.name},fields=['css_text','column_class'])
				for column in sec_columns:
					webtheme_css+= "."+x.class_name+" " +column.css_text
				for field in section_content:
					if field.css_text:
						webtheme_css+=field.css_text
			if page.edit_header_style == 1:
				if page.is_transparent_header == 1:
					p_route = page.route
					if "/" in p_route:
						p_route = p_route.split('/')[1]
					webtheme_css+="."+p_route+" .go1-cms-header{background:transparent;}"
					webtheme_css+="."+p_route+" .go1-cms-menu li a{color:"+page.menu_text_color+";}"
					if page.menu_hover_bg:
						webtheme_css+="."+p_route+" .go1-cms-menu li a:hover{background-color:"+page.menu_hover_bg+";}"
					if page.menu_hover_text_color:
						webtheme_css+="."+p_route+" .go1-cms-menu li a:hover{color:"+page.menu_hover_text_color+";}"
					if header_settings:
						webtheme_css+="."+p_route+" .sticky_header .go1-cms-menu li a{color:"+header_settings.menu_text_color+";}"
						webtheme_css+="."+p_route+" .sticky_header .go1-cms-menu li a:hover{color:"+header_settings.menu_hover_color+";}"
					else:
						if is_custom_header:
							if doc_obj.header_settings:
								webtheme_css+="."+p_route+" .sticky_header .go1-cms-menu li a{color:"+doc_obj.header_settings.menu_text_color+";}"
								webtheme_css+="."+p_route+" .sticky_header .go1-cms-menu li a:hover{color:"+doc_obj.header_settings.menu_hover_color+";}"
							
		if not os.path.exists(os.path.join(path,css_file_name)):
			res = frappe.get_doc({
						"doctype": "File",
						"file_name": css_file_name,
						"is_private": 1,
						})
		# frappe.log_error(webtheme_css,"<< webtheme_css >>")
		if webtheme_css:
			with open(os.path.join(path,(css_file_name)), "w") as f:
				f.write(minify_string(webtheme_css))
		fpath = os.path.join(path,(css_file_name))
		if self.file_path != fpath:
			frappe.db.set_value('Web Theme', self.name, 'file_path', fpath)
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.generate_webtheme_css_file")

def replace_value_of_globalfonts(css_design,doc_obj):
	if not css_design:
		return ""
	try:
		design_str = json.loads(css_design)
	except Exception:
		design_str = css_design
	api_css_parse_data = design_str.split(";")
	# frappe.log_error(json.loads(css_design),">>Received data<<")
	del api_css_parse_data[-1]
	# frappe.log_error(api_css_parse_data,">> splited data <<")
	for idxx,k in enumerate(api_css_parse_data):
		each_arr = k.split(":")
		if each_arr and len(each_arr) ==2:
			if(each_arr[1]) == "Primary(Font Family)":
				if doc_obj.primary_font_family:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.primary_font_family
				else:
					del api_css_parse_data[idxx]
			elif(each_arr[1]) == "Secondary(Font Family)":
				if doc_obj.secondary_font_family:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.secondary_font_family
				else:
					del api_css_parse_data[idxx]
			elif(each_arr[1]) == "Text(Font Family)":
				if doc_obj.text_font_family:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.text_font_family
				else:
					del api_css_parse_data[idxx]

			elif(each_arr[1]) == "Accent(Font Family)":
				if doc_obj.accent_font_family:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.accent_font_family
				else:
					del api_css_parse_data[idxx]

			if(each_arr[1]) == "Primary(Font Weight)":
				if doc_obj.primary_font_weight:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.primary_font_weight
				else:
					del api_css_parse_data[idxx]
			elif(each_arr[1]) == "Secondary(Font Weight)":
				if doc_obj.secondary_font_weight:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.secondary_font_weight
				else:
					del api_css_parse_data[idxx]
			elif(each_arr[1]) == "Text(Font Weight)":
				if doc_obj.text_font_weight:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.text_font_weight
				else:
					del api_css_parse_data[idxx]
			elif(each_arr[1]) == "Accent(Font Weight)":
				if doc_obj.accent_font_weight:
					api_css_parse_data[idxx] = each_arr[0] +':'+doc_obj.accent_font_weight
				else:
					del api_css_parse_data[idxx]
	# frappe.log_error(";".join(api_css_parse_data)+';',">> after replace global font family<<")
	return ";".join(api_css_parse_data)+';' if len(api_css_parse_data) > 0 else ""


# def get_absolute_path(file_name):
# 	# frappe.log_error(file_name,">>doc file name<<")
# 	temp_file_name = ""
# 	file_path_type =""
# 	if(file_name.startswith('/files/')):
# 		file_path_type = 'public'
# 		temp_file_name = file_name[7:]
# 	if(file_name.startswith('/private/')):
# 		file_path_type ='private'
# 		temp_file_name = file_name[15:]
# 	if(file_name.startswith('/public/')):
# 		file_path_type ='public'
# 		temp_file_name = file_name[14:]
# 	# frappe.log_error(temp_file_name,"file_name")
# 	# frappe.log_error(file_path_type,"file_path_type")
# 	if file_name and file_name.endswith(".css") and temp_file_name and file_path_type:
# 		return frappe.utils.get_bench_path()+ "/sites/" + frappe.utils.get_path(file_path_type,'files', temp_file_name)[2:]
# 	elif 'http' in file_name:
# 		return file_name
# 	else:
# 		return ""

@frappe.whitelist()
def get_cms_json():
	try:
		final_data = {}
		result = frappe.db.get_single_value('CMS Settings', 'styles_to_update')
		if result:
			final_data["cms_data"] = json.loads(result)
		else:
			final_data["cms_data"] = []
		fonts = frappe.db.get_list("CSS Font",fields=["font_family","font_family_category","font_name","font_type","font_url","name"])
		if fonts:
			final_data["font_data"] = fonts
		else:
			final_data["font_data"] = []
		return final_data
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_cms_json")


@frappe.whitelist()
def get_json_render_properties(field_type):
	try:
		css_properties = frappe.db.get_all("Field Types Property",filters={"field_type":field_type},fields=['css_properties_list'])
		# frappe.log_error(css_properties,"css_properties")
		if css_properties:
			css_properties[0].class_name = make_random_class_name()
			if css_properties[0].css_properties_list and len(css_properties[0].css_properties_list) > 0:
				css_properties[0].css_properties_list = json.loads(css_properties[0].css_properties_list)

			fonts_list = frappe.db.get_all("CSS Font",fields=['name','font_family'])
			if fonts_list:
				css_properties[0].fonts_list = fonts_list
			# frappe.log_error(css_properties,"fields")
		return css_properties
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_json_render_properties")

def make_random_class_name():
	try:
		import string
		import random
		res = ''.join(random.choices(string.ascii_lowercase, k = 8))
		return res
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.make_random_class_name")

@frappe.whitelist()
def get_color_palette_datas():
	try:
		all_palate_data = frappe.db.get_list("Color Palette",fields=["name","name1","image","body_text_color","accent_color","dark_color","secondary_color","heading_text_color","light_color","primary_color"],filters={"is_active":1})
		return all_palate_data
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_color_palette_datas")

@frappe.whitelist()
def get_color_palette_default_datas(palette_id):
	try:
		query_1 = ''' SELECT dc.type,dc.css_design,dc.style_json FROM `tabColor Palette` cp INNER JOIN `tabTypography Default Color` dc ON dc.parent=cp.name WHERE cp.name="%s"'''%palette_id
		return frappe.db.sql(query_1,as_dict=1)
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_color_palette_default_datas")
# end

@frappe.whitelist()
def get_color_code_data(bg_type):
	try:
		if bg_type == "Gradient":
			query_1 = ''' SELECT title,css_properties FROM `tabBackground Gradient`'''
		elif bg_type == "Pattern":
			query_1 = ''' SELECT title,css_properties FROM `tabBackground Pattern`'''
		elif bg_type == "Mask":
			query_1 = ''' SELECT title,css_properties FROM `tabBackground Mask`'''
		elif bg_type == "Divider":
			query_1 = ''' SELECT title,svg_file as css_properties FROM `tabSection Dividers`'''
		return frappe.db.sql(query_1,as_dict=1)
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.def get_color_code_data")
# end

@frappe.whitelist()
def get_style_guide_data():
	try:
		theme = frappe.db.get_value("Web Theme", {"is_active": 1}, "name")
		if not theme:
			return {}
		doc = frappe.get_doc("Web Theme", theme)
		colors = {
			"primary_color": doc.primary_color or "",
			"secondary_color": doc.secondary_color or "",
			"accent_color": doc.accent_color or "",
			"heading_text_color": doc.heading_text_color or "",
			"body_text_color": doc.body_text_color or "",
			"dark_color": doc.dark_color or "",
			"light_color": doc.light_color or "",
		}
		headings = [{"name": r.name, "name1": r.name1, "type": r.type, "css_design": r.css_design, "style_json": r.style_json} for r in doc.heading]
		texts = [{"name": r.name, "name1": r.name1, "type": r.type, "css_design": r.css_design, "style_json": r.style_json} for r in doc.text]
		fonts = [{"title": r.title, "font_family": r.font_family, "font_weight": r.font_weight} for r in doc.global_fonts]
		return {"colors": colors, "headings": headings, "texts": texts, "fonts": fonts, "theme": theme}
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_style_guide_data")
		return {}

@frappe.whitelist(allow_guest=True)
def get_theme_colors():
	try:
		theme_name = frappe.db.get_value("Web Theme", {"is_active": 1}, "name")
		if not theme_name:
			return {}
		doc = frappe.get_doc("Web Theme", theme_name)
		return {
			"primary_color": doc.primary_color or "",
			"secondary_color": doc.secondary_color or "",
			"accent_color": doc.accent_color or "",
			"heading_text_color": doc.heading_text_color or "",
			"body_text_color": doc.body_text_color or "",
			"dark_color": doc.dark_color or "",
			"light_color": doc.light_color or "",
			"body_background_color": doc.body_background_color or "",
			"border_radius": doc.get("border_radius") or ""
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms: get_theme_colors")
		return {}

@frappe.whitelist(allow_guest=True)
def get_theme_typography():
	try:
		theme_name = frappe.db.get_value("Web Theme", {"is_active": 1}, "name")
		if not theme_name:
			return {}
		doc = frappe.get_doc("Web Theme", theme_name)
		
		# Resolve global font names
		primary_font = ""
		text_font = ""
		if doc.global_fonts:
			for fonts in doc.global_fonts:
				if fonts.title == "Primary":
					primary_font = fonts.font_family or ""
				elif fonts.title == "Text":
					text_font = fonts.font_family or ""

		result = {}
		heading_map = {"h1": "heading-1", "h2": "heading-2", "h3": "heading-3"}
		for row in (doc.heading or []):
			key = heading_map.get(row.type)
			if key:
				style = json.loads(row.style_json) if row.style_json else {}
				if style.get("font-family") == "Primary(Font Family)" and primary_font:
					style["font-family"] = primary_font
				result[key] = {"style_json": json.dumps(style)}
		for row in (doc.text or []):
			if (row.type or "").split(" - ")[0].strip() == "p":
				style = json.loads(row.style_json) if row.style_json else {}
				if style.get("font-family") == "Text(Font Family)" and text_font:
					style["font-family"] = text_font
				result["body-text"] = {"style_json": json.dumps(style)}
		return result
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms: get_theme_typography")
		return {}

@frappe.whitelist(allow_guest=True)
def get_theme_css():
	try:
		theme_name = frappe.db.get_value("Web Theme", {"is_active": 1}, "name")
		if not theme_name:
			return ""
		return frappe.db.get_value("Web Theme", theme_name, "page_css") or ""
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms: get_theme_css")
		return ""

@frappe.whitelist()
def save_color_palette(name, name1, primary_color, secondary_color, accent_color,
                       heading_text_color, body_text_color, dark_color, light_color):
	try:
		if name:
			doc = frappe.get_doc("Color Palette", name)
		else:
			doc = frappe.new_doc("Color Palette")
		doc.name1 = name1
		doc.primary_color = primary_color
		doc.secondary_color = secondary_color
		doc.accent_color = accent_color
		doc.heading_text_color = heading_text_color
		doc.body_text_color = body_text_color
		doc.dark_color = dark_color
		doc.light_color = light_color
		doc.is_active = 1
		doc.save(ignore_permissions=True)
		# Apply to active web theme
		theme_name = frappe.db.get_value("Web Theme", {"is_active": 1}, "name")
		if theme_name:
			theme = frappe.get_doc("Web Theme", theme_name)
			theme.primary_color = primary_color
			theme.secondary_color = secondary_color
			theme.accent_color = accent_color
			theme.heading_text_color = heading_text_color
			theme.body_text_color = body_text_color
			theme.dark_color = dark_color
			theme.light_color = light_color
			theme.save(ignore_permissions=True)
		return doc.name
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.save_color_palette")
		return None

@frappe.whitelist()
def get_all_color_palettes():
	try:
		return frappe.db.get_list("Color Palette",
			fields=["name","name1","is_active","primary_color","secondary_color",
					"accent_color","heading_text_color","body_text_color","dark_color","light_color"],
			order_by="modified desc") or []
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_all_color_palettes")
		return []

@frappe.whitelist()
def delete_color_palette(name):
	try:
		is_active = frappe.db.get_value("Color Palette", name, "is_active")
		if is_active == 1:
			return {"status": "error", "message": "Cannot delete the active palette"}
		frappe.delete_doc("Color Palette", name, ignore_permissions=True)
		frappe.db.commit()
		return {"status": "success"}
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.delete_color_palette")
		return {"status": "error", "message": str(frappe.get_traceback())}

@frappe.whitelist()
def set_active_palette(name):
	try:
		frappe.db.sql("UPDATE `tabColor Palette` SET is_active=0 WHERE name != %s", name)
		frappe.db.set_value("Color Palette", name, "is_active", 1)
		frappe.db.commit()

		palette = frappe.get_doc("Color Palette", name)
		theme_name = frappe.db.get_value("Web Theme", {"is_active": 1}, "name")

		if theme_name:
			theme = frappe.get_doc("Web Theme", theme_name)
			theme.primary_color = palette.primary_color
			theme.secondary_color = palette.secondary_color
			theme.accent_color = palette.accent_color
			theme.heading_text_color = palette.heading_text_color
			theme.body_text_color = palette.body_text_color
			theme.dark_color = palette.dark_color
			theme.light_color = palette.light_color
			theme.save(ignore_permissions=True)

		return {"status": "success", "colors": {
			"primary_color": palette.primary_color,
			"secondary_color": palette.secondary_color,
			"accent_color": palette.accent_color,
			"heading_text_color": palette.heading_text_color,
			"body_text_color": palette.body_text_color,
			"dark_color": palette.dark_color,
			"light_color": palette.light_color
		}}
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.set_active_palette")
		return {"status": "error"}

@frappe.whitelist()
def get_css_fonts_list():
	try:
		return frappe.db.get_list("CSS Font",
			fields=["name","font_name","font_family"], order_by="font_name asc") or []
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.get_css_fonts_list")
		return []

@frappe.whitelist()
def save_typography_row(theme, row_name, parent_field, style_json, css_design):
	try:
		if parent_field not in ("heading", "text"):
			return {"status": "error", "message": "Invalid parent_field"}

		import json
		doc = frappe.get_doc("Web Theme", theme)
		child_table = doc.heading if parent_field == "heading" else doc.text

		found = False
		for row in child_table:
			if row.name == row_name:
				row.style_json = style_json
				row.css_design = json.dumps(css_design)
				found = True
				break

		if not found:
			return {"status": "error", "message": "Row not found"}

		doc.save(ignore_permissions=True)
		return {"status": "success"}
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.web_theme.web_theme.save_typography_row")
		return {"status": "error", "message": str(frappe.get_traceback())}
