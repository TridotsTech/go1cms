# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.website.website_generator import WebsiteGenerator
from frappe.query_builder import DocType
from go1_cms.utils.setup import get_settings_from_domain
class SectionComponent(WebsiteGenerator):
	def validate(self):
		if not self.route:
			self.route = self.scrub(self.title)

@frappe.whitelist()
def get_css_fields():
	cms_settings=get_settings_from_domain("CMS Settings", business=self.business)
	styles_to_update=cms_settings.styles_to_update
	
	return json.loads(styles_to_update)

@frappe.whitelist()
def get_component_details():
	try:
		group_data =[]
		section_component_group = DocType('Section Component Group')
		groups = (
			frappe.qb.from_(section_component_group)
			.select(section_component_group.group_name)
		).run(as_dict=True)
		# frappe.log_error(groups,">> groups <<")
		for each_grp in groups:
			section_component = DocType('Section Component')
			each_data = (
				frappe.qb.from_(section_component)
				.select(
					section_component.name.as_('unique_id'),
					section_component.group_name,
					section_component.allow_update_to_style,
					section_component.css_field_list,
					section_component.title.as_('name'),
					section_component.icon.as_('image'),
					section_component.css_field_list
				)
				.where(section_component.group_name == each_grp.group_name)
			).run(as_dict=True)
			if each_data and len(each_data) > 0:
				for k in each_data:
					group_data.append(k)
		return {"template_groups":groups,"templates":group_data}
	except Exception:
		frappe.log_error(frappe.get_traceback(),"go1_cms.go1_cms.doctype.section_component.section_component.get_component_details")