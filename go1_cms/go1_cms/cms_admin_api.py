# -*- coding: utf-8 -*-
# Copyright (c) 2024
# CMS Section Content Management API
# Enhanced API for frontend admin interface to manage section content

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import cstr

@frappe.whitelist(allow_guest=False)
def get_admin_section_info(section_id, page_builder_id):
	"""
	Get comprehensive section information for admin interface
	Includes content fields, properties, and styling options
	
	Args:
		section_id: Page Section ID
		page_builder_id: Web Page Builder ID
	
	Returns:
		dict with section info, content, properties
	"""
	try:
		# Check user permissions
		user = frappe.session.user
		if user == 'Guest':
			frappe.throw('Access Denied', frappe.PermissionError)
		
		# Verify user is admin
		user_roles = frappe.get_roles(user)
		if 'System Manager' not in user_roles and 'Administrator' not in user_roles and 'CMS Admin' not in user_roles:
			frappe.throw('You do not have permission to edit this content', frappe.PermissionError)
		
		# Get section info
		section = frappe.db.get_all(
			'Page Section',
			filters={'name': section_id},
			fields=[
				'name', 'section_type', 'section_title', 'reference_document',
				'fetch_product', 'reference_name', 'no_of_records',
				'custom_section_data', 'display_data_randomly', 'dynamic_data',
				'is_login_required', 'allow_update_to_style', 'menu',
				'class_name', 'css_json', 'is_full_width', 'css_text',
				'web_template', 'mobile_view_template', 'custom_css', 'custom_js'
			]
		)
		
		if not section:
			frappe.throw('Section not found', frappe.DoesNotExistError)
		
		section_info = section[0]
		
		# Get section content fields
		content_fields = frappe.db.sql('''
			SELECT 
				name, field_label, field_key, field_type, content,
				allow_update_to_style, css_properties_list, group_name,
				fields_json, css_json, css_text, image_dimension, idx
			FROM `tabSection Content`
			WHERE parent = %(parent)s AND content_type = 'Data' AND parenttype = 'Page Section'
			ORDER BY idx, field_key
		''', {'parent': section_id}, as_dict=1)
		
		# Parse JSON fields
		for field in content_fields:
			if field.get('css_properties_list'):
				try:
					field['css_properties_list'] = json.loads(field['css_properties_list'])
				except:
					field['css_properties_list'] = []
			
			if field.get('fields_json'):
				try:
					field['fields_json'] = json.loads(field['fields_json'])
				except:
					field['fields_json'] = {}
			
			if field.get('css_json'):
				try:
					field['css_json'] = json.loads(field['css_json'])
				except:
					field['css_json'] = {}
		
		# Parse section CSS if exists
		if section_info.get('css_json'):
			try:
				section_info['css_json'] = json.loads(section_info['css_json'])
			except:
				section_info['css_json'] = {}
		
		# Get fonts list
		fonts_list = frappe.db.get_all(
			'CSS Font',
			fields=['name', 'font_family', 'font_type', 'font_url']
		)
		
		return {
			'status': 'success',
			'section': section_info,
			'content_fields': content_fields,
			'fonts_list': fonts_list,
			'page_builder_id': page_builder_id
		}
	
	except frappe.PermissionError as e:
		frappe.log_error(frappe.get_traceback(), 'CMS Admin Permission Error')
		return {
			'status': 'error',
			'message': str(e)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'CMS Admin Section Info Error')
		return {
			'status': 'error',
			'message': 'Error fetching section info: ' + str(e)
		}


@frappe.whitelist(allow_guest=False)
def update_admin_section_content(section_id, page_builder_id, content_updates, css_updates=None):
	"""
	Update section content and styling from admin interface
	Handles validation and permission checking
	
	Args:
		section_id: Page Section ID
		page_builder_id: Web Page Builder ID
		content_updates: JSON string with field updates {field_key: value}
		css_updates: JSON string with CSS updates {css_text, is_full_width}
	
	Returns:
		dict with update status
	"""
	try:
		# Check user permissions
		user = frappe.session.user
		if user == 'Guest':
			frappe.throw('Access Denied', frappe.PermissionError)
		
		# Verify user is admin
		user_roles = frappe.get_roles(user)
		if 'System Manager' not in user_roles and 'Administrator' not in user_roles and 'CMS Admin' not in user_roles:
			frappe.throw('You do not have permission to edit this content', frappe.PermissionError)
		
		# Parse updates
		updates = json.loads(content_updates) if isinstance(content_updates, str) else content_updates
		css_updates = json.loads(css_updates) if isinstance(css_updates, str) else css_updates or {}
		
		# Get all content fields for this section
		content_fields = frappe.db.get_all(
			'Section Content',
			filters={'parent': section_id, 'parenttype': 'Page Section', 'content_type': 'Data'},
			fields=['name', 'field_key', 'field_type']
		)
		
		# Map field_key to field name
		field_key_map = {field['field_key']: field['name'] for field in content_fields}
		
		# Update content fields
		for field_key, value in updates.items():
			if field_key in field_key_map:
				field_name = field_key_map[field_key]
				
				# Convert value to string if needed
				if isinstance(value, dict) or isinstance(value, list):
					value = json.dumps(value)
				
				frappe.db.set_value('Section Content', field_name, 'content', cstr(value))
		
		# Update CSS and section properties
		if css_updates:
			section = frappe.get_doc('Page Section', section_id)
			
			if 'css_text' in css_updates:
				section.css_text = css_updates.get('css_text', '')
			
			if 'is_full_width' in css_updates:
				section.is_full_width = 1 if css_updates.get('is_full_width') else 0
			
			if 'css_json' in css_updates:
				section.css_json = json.dumps(css_updates.get('css_json', {}))
			
			section.save(ignore_permissions=True)
		
		# Trigger Page Section save to regenerate static JSON cache via on_update hook
		frappe.get_doc('Page Section', section_id).save(ignore_permissions=True)
		
		frappe.db.commit()
		
		# Log the action
		frappe.log_error(f'Section content updated by {user}: {section_id}', 'CMS Admin Update')
		
		return {
			'status': 'success',
			'message': 'Section content updated successfully',
			'section_id': section_id
		}
	
	except frappe.PermissionError as e:
		frappe.log_error(frappe.get_traceback(), 'CMS Admin Update Permission Error')
		return {
			'status': 'error',
			'message': str(e)
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'CMS Admin Update Error')
		return {
			'status': 'error',
			'message': 'Error updating section: ' + str(e)
		}


@frappe.whitelist(allow_guest=False)
def upload_section_asset(file_content, section_id, field_name):
	"""
	Upload an asset (image/file) for section content
	
	Args:
		file_content: Base64 encoded file content
		section_id: Page Section ID
		field_name: Field name to attach to
	
	Returns:
		dict with file URL
	"""
	try:
		user = frappe.session.user
		if user == 'Guest':
			frappe.throw('Access Denied', frappe.PermissionError)
		
		from frappe.utils import file_manager
		from PIL import Image
		from io import BytesIO
		import base64
		
		# Decode file
		file_parts = file_content.split(',')
		file_type = file_parts[0].split(':')[1].split(';')[0] if len(file_parts) > 0 else 'image/png'
		file_data = base64.b64decode(file_parts[1]) if len(file_parts) > 1 else base64.b64decode(file_content)
		
		# Generate filename
		filename = f'{section_id}_{field_name}_{frappe.utils.random_string(8)}.png'
		
		# Save file
		result = file_manager.save_file(filename, file_data, 'Section Content', section_id, is_private=False)
		
		return {
			'status': 'success',
			'file_url': result.file_url
		}
	
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'CMS Asset Upload Error')
		return {
			'status': 'error',
			'message': 'Error uploading file: ' + str(e)
		}


@frappe.whitelist(allow_guest=False)
def get_section_history(section_id, limit=10):
	"""
	Get update history for a section
	
	Args:
		section_id: Page Section ID
		limit: Number of recent updates to fetch
	
	Returns:
		list of recent updates
	"""
	try:
		# This could be enhanced with actual audit logging
		# For now, returns document version history
		history = frappe.db.get_all(
			'Document',
			filters={
				'doc': section_id,
				'doctype': 'Page Section'
			},
			fields=['name', 'created', 'modified_by', 'created_by'],
			order_by='modified desc',
			limit_page_length=limit
		)
		
		return {
			'status': 'success',
			'history': history
		}
	
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'CMS History Error')
		return {
			'status': 'error',
			'message': str(e)
		}
