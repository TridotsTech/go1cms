# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os
from frappe.model.document import Document
from frappe.utils import get_files_path

class MediaSettings(Document):
	def on_update(self):
		if self.default_image and self.default_image.find('/assets/') == -1:
			convert_product_image(self.default_image,self.detail_thumbnail_size,self.name)			
			file_name=self.default_image.split('.')
			self.detail_thumbnail=file_name[0]+"_"+str(self.detail_thumbnail_size)+"x"+str(self.detail_thumbnail_size)+"."+file_name[len(file_name)-1]

			# list_thumbnail
			convert_product_image(self.default_image,self.list_thumbnail_size,self.name)
			self.list_thumbnail=file_name[0]+"_"+str(self.list_thumbnail_size)+"x"+str(self.list_thumbnail_size)+"."+file_name[len(file_name)-1]
			
			# email_thumbnail
			convert_product_image(self.default_image,self.email_thumbnail_size,self.name)
			self.email_thumbnail=file_name[0]+"_"+str(self.email_thumbnail_size)+"x"+str(self.email_thumbnail_size)+"."+file_name[len(file_name)-1]
			
			# mini_cart_thumbnail
			convert_product_image(self.default_image,self.mini_cart_image_size,self.name)
			self.mini_cart_thumbnail=file_name[0]+"_"+str(self.mini_cart_image_size)+"x"+str(self.mini_cart_image_size)+"."+file_name[len(file_name)-1]
			
			# cart_thumbnail
			convert_product_image(self.default_image,self.cart_thumbnail_size,self.name)
			self.cart_thumbnail=file_name[0]+"_"+str(self.cart_thumbnail_size)+"x"+str(self.cart_thumbnail_size)+"."+file_name[len(file_name)-1]
		self.update_settings()

	def update_settings(self):
		path = get_files_path()
		if not os.path.exists(os.path.join(path,'settings')):
			frappe.create_folder(os.path.join(path,'settings'))
		if not os.path.exists(os.path.join(path,'settings', 'media')):
			frappe.create_folder(os.path.join(path,'settings', 'media'))
		with open(os.path.join(path,'settings', 'media', self.name.lower() + '.json'), "w") as f:
			f.write(frappe.as_json(self))

def convert_product_image(image_name,size,productid):
	try:
		image_file=image_name.split('.')
		image_file_name=image_file[0]+"_"+str(size)+"x"+str(size)+"."+image_file[1]
		org_file_doc = frappe.get_doc("File", {
					"file_url": image_name,
					"attached_to_doctype": "Media Settings",
					"attached_to_name": productid
				})
		if org_file_doc:
			org_file_doc.make_thumbnail(set_as_thumbnail=False,width=size,height=size,suffix=str(size)+"x"+str(size))
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store.ecommerce_business_store.doctype.product_category.convert_product_image") 
