# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals


import frappe
import unittest
import frappe.utils

test_records = frappe.get_test_records('Business')

class TestBusiness(unittest.TestCase):
	def test_business_creation(self):
		business1 = make_business("test_business_1@test.com", "1234561234", "Admin1", "Test Business 1")
		business2 = make_business("test_business_2@test.com", "1234561235", "Admin2", "Test Business 2")
		business1_doc = frappe.get_doc("Business", business1)
		business2_doc = frappe.get_doc("Business", business2)
		business2_doc.reload()
		business1_doc.reload()
		

def make_business(contact_email, phone, contact_person, business=None):
	if not frappe.db.get_value("Business", { "restaurant_name": business, "contact_email":contact_email}):
		bus = frappe.get_doc({
			"doctype": "Business",
			"restaurant_name": business,
			"contact_email": contact_email,
			"business_phone": phone,
			"contact_person": contact_person,
			"contact_number": phone,
			"country": "India"
		}).insert()
		return bus.name
	else:
		return frappe.get_value("Business", {"restaurant_name": business, "contact_email":contact_email}, "name")
