# Copyright (c) 2026, Tridotstech and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from go1_cms.go1_cms import business


def _project(name):
	return frappe.get_doc({"doctype": "CMS Project", "project_name": name, "project_slug": name.lower().replace(" ", "-")}).insert(
		ignore_permissions=True
	)


class TestBusiness(FrappeTestCase):
	def setUp(self):
		business.clear_cache()
		self.a = _project("Biz Test A")
		self.b = _project("Biz Test B")

	def tearDown(self):
		frappe.db.rollback()
		business.clear_cache()  # the cache outlives the rollback

	def test_every_project_gets_a_business(self):
		self.assertEqual(frappe.db.get_value("Business", {"project": self.a.name}, "name"), self.a.name)
		self.assertEqual(business.business_for_project(self.a.name), self.a.name)
		self.assertEqual(frappe.db.get_value("Business", self.a.name, "status"), "Active")

	def test_archiving_a_project_archives_its_business(self):
		self.a.status = "Archived"
		self.a.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Business", self.a.name, "status"), "Archived")
		self.a.status = "In Progress"
		self.a.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("Business", self.a.name, "status"), "Active")

	def test_domain_resolves_to_its_business(self):
		business.upsert_domain(self.a.name, "Acme.nvi.frappe.cloud", "platform_subdomain")
		business.upsert_domain(self.a.name, "www.acme.test", "custom_domain")
		hit = business.business_for_host("acme.nvi.frappe.cloud:8000")
		self.assertEqual((hit["business"], hit["project"]), (self.a.name, self.a.name))
		self.assertEqual(business.business_for_host("www.acme.test")["business"], self.a.name)
		# the first domain is the primary one; a later one can take over
		self.assertEqual(frappe.db.get_value("Business", self.a.name, "domain"), "acme.nvi.frappe.cloud")
		business.upsert_domain(self.a.name, "www.acme.test", "custom_domain", primary=True)
		self.assertEqual(frappe.db.get_value("Business", self.a.name, "domain"), "www.acme.test")
		self.assertIsNone(business.business_for_host("nobody.example"))

	def test_a_host_belongs_to_one_site(self):
		business.upsert_domain(self.a.name, "shared.example")
		with self.assertRaises(frappe.ValidationError):
			business.upsert_domain(self.b.name, "shared.example")

	def test_removed_domain_stops_resolving(self):
		business.upsert_domain(self.a.name, "gone.example")
		business.upsert_domain(self.a.name, "gone.example", remove=True)
		self.assertIsNone(business.business_for_host("gone.example"))
		self.assertIsNone(frappe.db.get_value("Business", self.a.name, "domain"))

	def test_rows_naming_a_project_are_stamped(self):
		page = frappe.new_doc("Web Page Builder")
		page.project = self.b.name
		business.stamp(page)
		self.assertEqual(page.business, self.b.name)
		other = frappe.new_doc("Web Page Builder")
		business.stamp(other)  # no project, nothing to stamp
		self.assertFalse(other.get("business"))

	def test_get_site_data_is_scoped_to_the_domain(self):
		business.upsert_domain(self.a.name, "a.example")
		business.upsert_domain(self.b.name, "b.example")
		for project in (self.a, self.b):
			frappe.get_doc({"doctype": "Menu", "title": f"Menu of {project.name}", "project": project.name}).insert(ignore_permissions=True)
		rows = business.get_site_data("a.example", "Menu", ["title", "project", "business"])
		self.assertEqual([(r["title"], r["project"], r["business"]) for r in rows],
			[(f"Menu of {self.a.name}", self.a.name, self.a.name)])
		rows_b = business.get_site_data("b.example", "Menu", ["title"], {"title": ["like", "Menu of%"]})
		self.assertEqual([r["title"] for r in rows_b], [f"Menu of {self.b.name}"])
		with self.assertRaises(frappe.DoesNotExistError):
			business.get_site_data("nowhere.example", "Menu")
		with self.assertRaises(frappe.ValidationError):
			business.get_site_data("a.example", "User")  # not a site-scoped doctype
