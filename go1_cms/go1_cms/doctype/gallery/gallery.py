# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Gallery(Document):
	# pass
	def validate(self):
		try:
			if self.gallery:
				count = 1
				for d in self.gallery:
					cover_image = frappe.get_list("Gallery Files",filters={"name":d.name,"is_cover_image":1})
					if not cover_image and d.is_cover_image==1 and not self.cover_image:
						d.is_cover_image =1
					cover_images = [x for x in self.gallery if x.is_cover_image==1]
					if cover_image and len(cover_images)>1:
						d.is_cover_image = 0
						cover_image_checked =1
					if len(cover_images)==0 and count==1:
						d.is_cover_image =1
				if self.gallery:
					for d in self.gallery:
						if d.is_cover_image:
							self.cover_image = d.image__video

		except Exception as e:
			frappe.log_error(frappe.get_traceback(),"coverImages")




