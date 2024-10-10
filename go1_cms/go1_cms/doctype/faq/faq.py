# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FAQ(Document):
	def autoname(self): 
		naming_series="FAQ-"
		if self.business:
			abbr=frappe.db.get_value('Business',self.business,'abbr')
			if abbr:
				naming_series+=abbr+'-'
		self.naming_series=naming_series
		from frappe.model.naming import make_autoname
		self.name = make_autoname(naming_series+'.#####', doc=self)