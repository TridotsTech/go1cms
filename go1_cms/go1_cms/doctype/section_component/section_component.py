# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.website.website_generator import WebsiteGenerator

class SectionComponent(WebsiteGenerator):
	def validate(self):
		if not self.route:
			self.route = self.scrub(self.title)

@frappe.whitelist()
def get_css_fields():
	result = frappe.db.get_single_value('CMS Settings', 'styles_to_update')
	return json.loads(result)

@frappe.whitelist()
def get_component_details():
	try:
		group_data =[]
		query_1 = ''' SELECT group_name FROM `tabSection Component Group`'''
		groups = frappe.db.sql(query_1,as_dict=1)
		# frappe.log_error(groups,">> groups <<")
		for each_grp in groups:
			# query_2 = ''' SELECT sc.name as unique_id,sc.title as name,sc.group_name as section_group,sc.icon,sc.preview_image as image,sc.allow_update_to_style,sc.css_field_list,sec.field_label,
			#  			  sec.field_key,sec.field_type,sec.content_type,sec.image_dimension,sec.allow_update_to_style,sec.css_properties_list,
			# 			  sec.content,sec.fields_json,sec.css_json,sec.css_text	FROM `tabSection Component` sc INNER JOIN `tabSection Content` sec ON sec.parent=sc.name WHERE sc.group_name="%s"'''%each_grp.group_name
			query_2 = ''' SELECT name as unique_id,group_name,allow_update_to_style,css_field_list,title as name,icon as image,css_field_list FROM `tabSection Component` WHERE group_name="%s"'''%each_grp.group_name
			each_data = frappe.db.sql(query_2,as_dict=1)	
			if each_data and len(each_data) > 0:
				for k in each_data:
					group_data.append(k)
		return {"template_groups":groups,"templates":group_data}
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.section_component.section_component.get_component_details")