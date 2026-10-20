"""Publishing: what goes live, what stays hidden, and what is logged (OPS-09).

    bench --site <site> run-tests --module go1_cms.go1_cms.tests.test_publishing
"""

import json

import frappe
from frappe.tests.utils import FrappeTestCase

from go1_cms.go1_cms import api
from go1_cms.go1_cms.tests.helpers import layout, make_page


class TestPublishing(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")

	def doc(self, name):
		return frappe.get_doc("Web Page Builder", name)

	def test_publish_copies_the_draft_live(self):
		page = make_page("zz-ops09 publish", "zz-ops09-publish", draft=layout("hello"))
		api.publish_page(page)
		doc = self.doc(page)
		self.assertEqual(doc.published, 1)
		self.assertIn("hello", doc.layout_json)

	def test_a_draft_alone_is_not_live(self):
		page = make_page("zz-ops09 draft", "zz-ops09-draft", draft=layout("secret"), live=layout("old"))
		doc = self.doc(page)
		self.assertEqual(doc.published, 0)
		self.assertNotIn("secret", doc.layout_json)

	def test_publish_with_nothing_to_publish_is_refused(self):
		page = make_page("zz-ops09 empty", "zz-ops09-empty")
		with self.assertRaises(frappe.ValidationError):
			api.publish_page(page)
		self.assertEqual(self.doc(page).published, 0)

	def test_publish_logs_who_and_keeps_the_previous_layout(self):
		page = make_page("zz-ops09 log", "zz-ops09-log", draft=layout("new"), live=layout("old"), published=1)
		api.publish_page(page, source="Project")
		row = frappe.get_all("Web Page Publish Log", filters={"page": page},
		                     fields=["published_by", "source", "previous_layout_json"], limit=1)[0]
		self.assertEqual(row.published_by, "Administrator")
		self.assertEqual(row.source, "Project")
		self.assertIn("old", row.previous_layout_json)

	def test_unpublish_hides_the_page_but_keeps_the_live_copy(self):
		page = make_page("zz-ops09 down", "zz-ops09-down", draft=layout("body"))
		api.publish_page(page)
		api.unpublish_page(page)
		doc = self.doc(page)
		self.assertEqual(doc.published, 0)
		self.assertIn("body", doc.layout_json)

	def test_unpublishing_a_page_that_is_not_live_does_nothing(self):
		page = make_page("zz-ops09 noop", "zz-ops09-noop", live=layout("x"))
		before = frappe.db.count("Web Page Publish Log", {"page": page})
		api.unpublish_page(page)
		self.assertEqual(frappe.db.count("Web Page Publish Log", {"page": page}), before)

	def test_republish_picks_up_pending_title_route_and_css(self):
		draft = json.loads(layout("v2"))
		draft["pending"] = {"page_title": "zz-ops09 renamed", "route": "zz-ops09-renamed", "custom_css": ".a{color:red}"}
		page = make_page("zz-ops09 pending", "zz-ops09-pending", draft=json.dumps(draft), live=layout("v1"), published=1)
		api.publish_page(page)
		doc = self.doc(page)
		self.assertEqual(doc.route, "zz-ops09-renamed")
		self.assertEqual(doc.custom_css, ".a{color:red}")
		self.assertNotIn("pending", json.loads(doc.layout_json))

	def test_missing_page_is_a_clean_not_found(self):
		with self.assertRaises(frappe.DoesNotExistError):
			api.publish_page("zz-ops09 does not exist")
