# Copyright (c) 2015, Tridotstech Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function

import frappe
import frappe, os, re
import json
import zipfile

def after_install():
	unzip_section_images()
	insert_header_layouts()
	insert_footer_layouts()
	insert_section_groups()
	insert_custom_queries()
	insert_section_templates()
	insert_color_palletes()
	insert_section_component_groups()
	insert_section_components()
	insert_cms_settings()
	insert_background_masks()
	insert_background_gradients()
	insert_css_fonts()
	insert_menus()
	insert_header_components()
	insert_footer_components()
	insert_web_theme()
	insert_faq()
	insert_testimonial()
	insert_webpage_builder()
	
def insert_css_fonts():
	file_name = "css_fonts.json"
	read_module_path(file_name)

def insert_menus():
	file_name = "menus.json"
	read_module_path(file_name)

def insert_header_layouts():
	file_name = "header_layouts.json"
	read_module_path(file_name)

def insert_section_components():
	file_name = "section_components.json"
	read_module_path(file_name)

def insert_section_component_groups():
	file_name = "section_component_groups.json"
	read_module_path(file_name)


def insert_footer_layouts():
	file_name = "footer_layouts.json"
	read_module_path(file_name)

def insert_section_groups():
	file_name = "section_groups.json"
	read_module_path(file_name)

def insert_custom_queries():
	file_name = "custom_query.json"
	read_module_path(file_name)

def insert_section_templates():
	file_name = "section_templates.json"
	read_module_path(file_name)

def insert_color_palletes():
	file_name = "color_palletes.json"
	read_module_path(file_name)

def insert_cms_settings():
	file_name = "cms_settings.json"
	read_module_path(file_name)

def insert_background_masks():
	file_name = "background_masks.json"
	read_module_path(file_name)

def insert_background_gradients():
	file_name = "background_gradients.json"
	read_module_path(file_name)

def insert_web_theme():
	file_name = "web_themes.json"
	read_module_path(file_name)

def insert_faq():
	file_name = "faq.json"
	read_module_path(file_name)

def insert_testimonial():
	file_name = "testimonial.json"
	read_module_path(file_name)


def insert_webpage_builder():
	pass
	# path = frappe.get_module_path("go1_cms")
	# from frappe.model.mapper import get_mapped_doc
	# file_path = os.path.join(path,'json_data',"header_components.json")
	# if os.path.exists(file_path):
	# 	with open(file_path, 'r') as f:
	# 		out = json.load(f)
	# 	for i in out:
	# 		try:
	# 			doc = frappe.get_doc(i).insert()
	# 			web_sections = i.get("web_section")
	# 			header_sec_file_path = os.path.join(path,'json_data',"header_sections.json")
	# 			if os.path.exists(header_sec_file_path):
	# 				with open(header_sec_file_path, 'r') as f:
	# 					header_out = json.load(f)
	# 				for j in header_out:
	# 					template = section_name = j.get("section_title")
	# 					p_doc = get_mapped_doc("Section Template", template, {
	# 						"Section Template": {
	# 							"doctype": "Page Section"
	# 						},
	# 						"Section Content":{
	# 							"doctype": "Section Content"
	# 						}
	# 					}, None, ignore_permissions=True)
	# 					p_doc.section_title = template
	# 					p_doc.custom_title = section_name
	# 					p_doc.choose_from_template = 1
	# 					p_doc.section_template = template
	# 					if j.get("section_type") == "Menu":
	# 						p_doc.menu = j.get("menu")
	# 					p_doc.save(ignore_permissions=True)
	# 					doc.append("web_section",{
	# 				        "idx": j.get("idx"),
	# 				        "docstatus": 0,
	# 				        "section": p_doc.name,
	# 				        "section_title": template,
	# 				        "section_type": j.get("section_type"),
	# 				        "allow_update_to_style": 0,
	# 				        "column_index": j.get("column_index"),
	# 						})
	# 			doc.save()
	# 		except frappe.NameError:
	# 			pass
	# 		except Exception as e:
	# 			frappe.log_error(frappe.get_traceback(), "Header Component Insertion") 



def insert_header_components():
	path = frappe.get_module_path("go1_cms")
	from frappe.model.mapper import get_mapped_doc
	file_path = os.path.join(path,'json_data',"header_components.json")
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			out = json.load(f)
		for i in out:
			try:
				doc = frappe.get_doc(i).insert()
				web_sections = i.get("web_section")
				header_sec_file_path = os.path.join(path,'json_data',"header_sections.json")
				if os.path.exists(header_sec_file_path):
					with open(header_sec_file_path, 'r') as f:
						header_out = json.load(f)
					for j in header_out:
						template = section_name = j.get("section_title")
						p_doc = get_mapped_doc("Section Template", template, {
							"Section Template": {
								"doctype": "Page Section"
							},
							"Section Content":{
								"doctype": "Section Content"
							}
						}, None, ignore_permissions=True)
						p_doc.section_title = template
						p_doc.custom_title = section_name
						p_doc.choose_from_template = 1
						p_doc.section_template = template
						if j.get("section_type") == "Menu":
							p_doc.menu = j.get("menu")
						p_doc.save(ignore_permissions=True)
						doc.append("web_section",{
					        "idx": j.get("idx"),
					        "docstatus": 0,
					        "section": p_doc.name,
					        "section_title": template,
					        "section_type": j.get("section_type"),
					        "allow_update_to_style": 0,
					        "column_index": j.get("column_index"),
							})
				doc.save()
			except frappe.NameError:
				pass
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), "Header Component Insertion")  
def insert_footer_components():
	path = frappe.get_module_path("go1_cms")
	from frappe.model.mapper import get_mapped_doc
	file_path = os.path.join(path,'json_data',"footer_components.json")
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			out = json.load(f)
		for i in out:
			try:
				doc = frappe.get_doc(i).insert()
				web_sections = i.get("web_section")
				header_sec_file_path = os.path.join(path,'json_data',"footer_sections.json")
				if os.path.exists(header_sec_file_path):
					with open(header_sec_file_path, 'r') as f:
						header_out = json.load(f)
					for j in header_out:
						template = section_name = j.get("section_title")
						p_doc = get_mapped_doc("Section Template", template, {
							"Section Template": {
								"doctype": "Page Section"
							},
							"Section Content":{
								"doctype": "Section Content"
							}
						}, None, ignore_permissions=True)
						p_doc.section_title = template
						p_doc.custom_title = section_name
						p_doc.choose_from_template = 1
						p_doc.section_template = template
						if j.get("section_type") == "Menu":
							p_doc.menu = j.get("menu")
						p_doc.save(ignore_permissions=True)
						doc.append("web_section",{
					        "idx": j.get("idx"),
					        "docstatus": 0,
					        "section": p_doc.name,
					        "section_title": template,
					        "section_type": j.get("section_type"),
					        "allow_update_to_style": 0,
					        "column_index": j.get("column_index"),
							})
				doc.save()
			except frappe.NameError:
				pass
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), "Footer Component Insertion")  

def read_module_path(file_name):
	path = frappe.get_module_path("go1_cms")
	file_path = os.path.join(path,'json_data',file_name)
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			out = json.load(f)
		for i in out:
			try:
				frappe.get_doc(i).insert()
			except frappe.NameError:
				pass
			except Exception as e:
				frappe.log_error(frappe.get_traceback(), file_name)   

def unzip_section_images():
	"""Unzip current file and replace it by its children"""
	path = frappe.get_module_path("go1_cms")
	file_path = os.path.join(path,"section_images.zip")
	with zipfile.ZipFile(file_path) as z:
		for file in z.filelist:
			if file.is_dir() or file.filename.startswith("__MACOSX/"):
				# skip directories and macos hidden directory
				continue
			filename = os.path.basename(file.filename)
			if filename.startswith("."):
				# skip hidden files
				continue
			file_doc = frappe.new_doc("File")
			file_doc.content = z.read(file.filename)
			file_doc.file_name = filename
			file_doc.folder = "Home"
			file_doc.is_private = 0
			file_doc.save()
