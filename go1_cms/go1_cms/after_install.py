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
	insert_section_components()

def insert_header_layouts():
	file_name = "header_layouts.json"
	read_module_path(file_name)

def insert_section_components():
	file_name = "section_components.json"
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
				pass   


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
