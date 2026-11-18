# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import re

import frappe
from frappe.model.document import Document


def make_gallery_route(title):
	"""'KRISHNA JEYANTHI 2026' -> 'gallery/krishna-jeyanthi-2026'"""
	slug = re.sub(r"['’]", "", (title or "").lower())
	slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
	return f"gallery/{slug}" if slug else None


class Gallery(Document):
	def validate(self):
		self.set_route()
		self.set_cover_image()

	def set_route(self):
		# Fill the route from the title only when it is empty, or on a new
		# gallery where it still holds the auto value. Existing routes are live
		# URLs, so they are never rewritten.
		base = make_gallery_route(self.title)
		if not base or (self.route and not (self.is_new() and self.route == base)):
			return
		route, n = base, 2
		while frappe.db.exists("Gallery", {"route": route, "name": ["!=", self.name]}):
			route, n = f"{base}-{n}", n + 1
		self.route = route

	def set_cover_image(self):
		try:
			if self.gallery:
				count = 1
				for d in self.gallery:
					cover_image = frappe.get_all("Gallery Files",filters={"name":d.name,"is_cover_image":1})
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




