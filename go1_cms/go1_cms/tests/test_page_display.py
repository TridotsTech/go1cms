"""Page display: which layout a visitor or an editor is served, and the query guards (OPS-09).

    bench --site <site> run-tests --module go1_cms.go1_cms.tests.test_page_display
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from go1_cms.go1_cms import api
from go1_cms.go1_cms.tests.helpers import layout, make_page, make_project, make_user

EDITOR = "zz-ops09-display-editor@example.com"


def texts(page_layout):
	return [c["content"] for s in page_layout["sections"] for c in s["children"]]


class TestPageDisplay(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		if not frappe.db.exists("Role", "Website Manager"):
			frappe.get_doc({"doctype": "Role", "role_name": "Website Manager"}).insert(ignore_permissions=True)
		make_user(EDITOR, "Website Manager")
		cls.project = make_project("zz-ops09 display", "zz-ops09-display", member=EDITOR)
		cls.live = make_page("zz-ops09 live", "zz-ops09-live", project=cls.project,
		                     draft=layout("draft v2"), live=layout("live v1"), published=1)
		cls.hidden = make_page("zz-ops09 hidden", "zz-ops09-hidden", project=cls.project,
		                       draft=layout("hidden draft"), live=layout("hidden live"), published=0)
		cls.blank = make_page("zz-ops09 blank", "zz-ops09-blank", project=cls.project, published=1)
		# A page's route is saved with its website's slug in front.
		route = lambda page: frappe.db.get_value("Web Page Builder", page, "route")
		cls.live_route, cls.hidden_route, cls.blank_route = route(cls.live), route(cls.hidden), route(cls.blank)

	def setUp(self):
		frappe.set_user("Guest")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.local.cpanel_project = None

	# ── visitors ──────────────────────────────────────────────────────────

	def test_a_visitor_sees_the_live_layout_not_the_draft(self):
		self.assertEqual(texts(api._fb2_load_page_layout(self.live_route)), ["live v1"])

	def test_a_visitor_cannot_force_the_draft(self):
		self.assertEqual(texts(api._fb2_load_page_layout(self.live_route, is_builder=1)), ["live v1"])

	def test_an_unpublished_page_is_refused_to_visitors(self):
		with self.assertRaises(frappe.PermissionError):
			api._fb2_load_page_layout(self.hidden_route)
		with self.assertRaises(frappe.PermissionError):
			api._fb2_load_page_layout(self.hidden_route, is_builder=1)

	def test_an_unknown_route_is_not_found(self):
		with self.assertRaises(frappe.DoesNotExistError):
			api._fb2_load_page_layout("zz-ops09-nope")

	def test_a_published_page_with_no_layout_is_not_found(self):
		with self.assertRaises(frappe.DoesNotExistError):
			api._fb2_load_page_layout(self.blank_route)

	def test_a_broken_layout_is_a_clean_error(self):
		frappe.set_user("Administrator")
		frappe.db.set_value("Web Page Builder", self.live, "layout_json", "{not json")
		frappe.set_user("Guest")
		with self.assertRaises(frappe.ValidationError):
			api._fb2_load_page_layout(self.live_route)
		frappe.db.set_value("Web Page Builder", self.live, "layout_json", layout("live v1"))

	# ── editors ───────────────────────────────────────────────────────────

	def test_an_editor_sees_the_draft_in_the_builder(self):
		frappe.set_user(EDITOR)
		self.assertEqual(texts(api._fb2_load_page_layout(self.live_route, is_builder=1)), ["draft v2"])
		self.assertEqual(texts(api._fb2_load_page_layout(self.hidden_route, is_builder=1)), ["hidden draft"])

	def test_an_editor_outside_the_website_still_gets_the_live_page_only(self):
		other = "zz-ops09-display-other@example.com"
		frappe.set_user("Administrator")
		make_user(other, "Website Manager")
		frappe.set_user(other)
		self.assertEqual(texts(api._fb2_load_page_layout(self.live_route, is_builder=1)), ["live v1"])

	# ── routes ────────────────────────────────────────────────────────────

	def test_route_forms_all_find_the_same_page(self):
		r = self.live_route
		for route in (r, "/" + r, "p/" + r, "/p/" + r, " " + r + "/ "):
			found = api.find_web_page_builder_by_route(route)
			self.assertTrue(found, route)
			self.assertEqual(found[0].name, self.live)

	def test_a_detail_url_falls_back_to_its_parent_page(self):
		found = api.find_web_page_builder_by_route(self.live_route + "/some-record")
		self.assertEqual(found[0].name, self.live)

	def test_a_wildcard_template_wins_over_the_parent_page(self):
		tmpl = make_page("zz-ops09 tmpl", self.live_route + "/*", project=self.project, live=layout("t"), published=1)
		found = api.find_web_page_builder_by_route(self.live_route + "/some-record")
		self.assertEqual(found[0].name, tmpl)
		self.assertEqual(api.find_web_page_builder_by_route(self.live_route)[0].name, self.live)

	def test_a_websites_own_domain_never_serves_another_websites_page(self):
		other = make_project("zz-ops09 other", "zz-ops09-other")
		frappe.local.cpanel_project = other
		self.assertFalse(api.find_web_page_builder_by_route(self.live_route))
		frappe.local.cpanel_project = self.project
		self.assertTrue(api.find_web_page_builder_by_route(self.live_route))

	def test_no_route_finds_nothing(self):
		self.assertIsNone(api.find_web_page_builder_by_route(""))
		self.assertIsNone(api.find_web_page_builder_by_route(None))

	# ── the query guards behind repeaters and lists ───────────────────────

	def test_field_names_are_plain_columns_only(self):
		self.assertEqual(api._fb2_sanitize_fields(["name", "title; drop table x", "ok_1"]), ["name", "ok_1"])
		self.assertEqual(api._fb2_sanitize_fields(["(select 1)"]), ["name"])
		self.assertEqual(api._fb2_sanitize_fields("*"), ["*"])

	def test_sort_order_cannot_carry_sql(self):
		self.assertEqual(api._fb2_order_by("creation", "desc"), "`creation` desc")
		self.assertEqual(api._fb2_order_by("creation", "sideways"), "`creation` asc")
		self.assertIsNone(api._fb2_order_by("creation; drop table x", "asc"))
		self.assertIsNone(api._fb2_order_by("", "asc"))

	def test_filters_keep_only_known_operators_on_real_columns(self):
		good = api._fb2_sanitize_filters([["status", "=", "Open"], ["name", "like", "a%"]])
		self.assertEqual(len(good), 2)
		self.assertEqual(api._fb2_sanitize_filters([["status", "union select", "x"]]), [])
		self.assertEqual(api._fb2_sanitize_filters([["st atus", "=", "x"]]), [])
		self.assertEqual(api._fb2_sanitize_filters([["status", "=", {"a": 1}]]), [])
		self.assertEqual(api._fb2_sanitize_filters({"bad col": 1, "status": "Open"}), {"status": "Open"})
		self.assertEqual(api._fb2_sanitize_filters(None), {})
		self.assertEqual(api._fb2_sanitize_filters("not json"), {})

	def test_in_filters_split_a_comma_list(self):
		self.assertEqual(api._fb2_sanitize_filters([["status", "in", "a, b ,c"]]), [["status", "in", ["a", "b", "c"]]])

	def test_search_terms_are_values_never_sql(self):
		rows = api._fb2_search_filters("Web Page Builder", ["page_title", "no_such_col", "x; drop"], "50%_off")
		self.assertEqual([r[0] for r in rows], ["page_title"])
		self.assertNotIn("%_", rows[0][2][1:-1])
		self.assertIsNone(api._fb2_search_filters("Web Page Builder", ["no_such_col"], "term"))
		self.assertIsNone(api._fb2_search_filters("Web Page Builder", ["page_title"], "   "))
