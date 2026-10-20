"""Permissions: who may edit which website, and who may see drafts (OPS-09).

    bench --site <site> run-tests --module go1_cms.go1_cms.tests.test_permissions
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from go1_cms.go1_cms import api, cms_access
from go1_cms.go1_cms.tests.helpers import layout, make_page, make_project, make_user

OWNER = "zz-ops09-owner@example.com"
OUTSIDER = "zz-ops09-outsider@example.com"
PLAIN = "zz-ops09-plain@example.com"


class TestPermissions(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		if not frappe.db.exists("Role", "Website Manager"):
			frappe.get_doc({"doctype": "Role", "role_name": "Website Manager"}).insert(ignore_permissions=True)
		make_user(OWNER, "Website Manager")
		make_user(OUTSIDER, "Website Manager")
		make_user(PLAIN)  # a signed-in user with no editing role
		cls.mine = make_project("zz-ops09 mine", "zz-ops09-mine", member=OWNER)
		cls.theirs = make_project("zz-ops09 theirs", "zz-ops09-theirs", member=OUTSIDER)
		cls.page = make_page("zz-ops09 mine page", "zz-ops09-mine-page", project=cls.mine,
		                     draft=layout("draft"), live=layout("live"), published=1)
		cls.loose = make_page("zz-ops09 loose page", "zz-ops09-loose-page", draft=layout("x"))

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	# ── who is an editor ──────────────────────────────────────────────────

	def test_editor_roles(self):
		self.assertTrue(cms_access.is_editor("Administrator"))
		self.assertTrue(cms_access.is_editor(OWNER))
		self.assertFalse(cms_access.is_editor(PLAIN))
		self.assertFalse(cms_access.is_editor("Guest"))

	def test_only_system_managers_see_every_project(self):
		self.assertTrue(cms_access.sees_all_projects("Administrator"))
		self.assertFalse(cms_access.sees_all_projects(OWNER))
		self.assertIsNone(cms_access.allowed_projects("Administrator"))

	def test_a_member_sees_only_their_own_websites(self):
		self.assertEqual(cms_access.allowed_projects(OWNER), [self.mine])
		self.assertEqual(cms_access.allowed_projects(OUTSIDER), [self.theirs])

	# ── pages ─────────────────────────────────────────────────────────────

	def test_member_may_open_their_page_but_not_another_websites(self):
		frappe.set_user(OWNER)
		cms_access.require_page(self.page)  # no error
		frappe.set_user(OUTSIDER)
		with self.assertRaises(frappe.PermissionError):
			cms_access.require_page(self.page)

	def test_a_page_with_no_website_is_for_system_managers_only(self):
		frappe.set_user(OWNER)
		with self.assertRaises(frappe.PermissionError):
			cms_access.require_page(self.loose)
		frappe.set_user("Administrator")
		cms_access.require_page(self.loose)

	def test_guest_and_plain_users_cannot_edit_anything(self):
		for user in ("Guest", PLAIN):
			frappe.set_user(user)
			with self.assertRaises(frappe.PermissionError):
				cms_access.require_page(self.page)
			with self.assertRaises(frappe.PermissionError):
				cms_access.require_project(self.mine)

	# ── publishing goes through the same gate ─────────────────────────────

	def test_outsider_cannot_publish_or_unpublish_someone_elses_page(self):
		frappe.set_user(OUTSIDER)
		with self.assertRaises(frappe.PermissionError):
			api.publish_page(self.page)
		with self.assertRaises(frappe.PermissionError):
			api.unpublish_page(self.page)
		self.assertEqual(frappe.db.get_value("Web Page Builder", self.page, "published"), 1)

	def test_member_can_unpublish_their_own_page(self):
		frappe.set_user(OWNER)
		api.unpublish_page(self.page)
		self.assertEqual(frappe.db.get_value("Web Page Builder", self.page, "published"), 0)
		frappe.db.set_value("Web Page Builder", self.page, "published", 1)

	def test_guest_cannot_publish(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			api.publish_page(self.page)

	# ── drafts ────────────────────────────────────────────────────────────

	def test_drafts_are_for_the_pages_own_editors(self):
		self.assertTrue(cms_access.can_see_draft(self.page, "Administrator"))
		self.assertTrue(cms_access.can_see_draft(self.page, OWNER))
		self.assertFalse(cms_access.can_see_draft(self.page, OUTSIDER))
		self.assertFalse(cms_access.can_see_draft(self.page, PLAIN))
		self.assertFalse(cms_access.can_see_draft(self.page, "Guest"))

	# ── the pages table itself ────────────────────────────────────────────

	def test_page_records_are_not_open_to_guests_or_website_managers_directly(self):
		self.assertFalse(frappe.has_permission("Web Page Builder", "read", user="Guest"))
		self.assertFalse(frappe.has_permission("Web Page Builder", "write", user=OWNER))
		self.assertTrue(frappe.has_permission("Web Page Builder", "write", user="Administrator"))

	def test_membership_never_downgrades_an_owner(self):
		cms_access.add_member(self.mine, OWNER, access="Editor")
		self.assertTrue(cms_access.is_project_owner(self.mine, OWNER))
