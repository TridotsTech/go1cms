"""Docs: slugs, nesting, rendering, and what a visitor may see.

    bench --site <site> run-tests --module go1_cms.docs.test_docs

Every row is created inside the test transaction under the space "zz-docs-test"
and rolled back by FrappeTestCase; nothing here commits.
"""

import frappe
from frappe.tests.utils import FrappeTestCase

from go1_cms.docs import api, render

SPACE = "zz-docs-test"
OTHER = "zz-docs-other"


def article(slug, space=SPACE, status="Published", body="Some text.", **kw):
	doc = frappe.get_doc({"doctype": "Doc Article", "title": slug.replace("-", " ").title(), "slug": slug,
	                      "space": space, "status": status, "body_md": body, **kw})
	doc.insert(ignore_permissions=True)
	return doc


class TestDocs(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		for slug, published in ((SPACE, 1), (OTHER, 0)):
			if not frappe.db.exists("Doc Space", slug):
				frappe.get_doc({"doctype": "Doc Space", "title": slug, "slug": slug, "is_published": published,
				                "sort_order": 999}).insert(ignore_permissions=True)
		api.clear_cache()

	def tearDown(self):
		frappe.set_user("Administrator")
		api.clear_cache()

	# ── rendering ─────────────────────────────────────────────────────────

	def test_render_outline_links_and_callouts(self):
		out = render.render("## One\n\nSee [two](../two#x).\n\n> [!WARNING]\n> Careful.\n\n### Sub\n", SPACE)
		self.assertIn('href="/docs/%s/two#x"' % SPACE, out["html"])
		self.assertIn('class="callout callout-warning"', out["html"])
		self.assertEqual([(h["level"], h["id"]) for h in out["outline"]], [(2, "one"), (3, "sub")])

	def test_render_strips_scripts_and_unsafe_iframes(self):
		out = render.render('a\n\n<script>alert(1)</script>\n\n<iframe src="https://evil.example/x"></iframe>\n\n'
		                    '<a href="javascript:alert(1)">x</a>', SPACE)
		self.assertNotIn("alert(1)", out["html"].replace("&lt;", "<").split("<a")[0])
		self.assertNotIn("<script", out["html"])
		self.assertNotIn("evil.example", out["html"])
		self.assertNotIn("javascript:", out["html"])

	def test_article_save_stores_rendered_body(self):
		doc = article("rendered", body="## Heading\n\nText **bold**.")
		self.assertIn("<strong>bold</strong>", doc.body_html)
		self.assertIn("Text bold.", doc.body_text)
		self.assertTrue(doc.published_on)

	# ── validation ────────────────────────────────────────────────────────

	def test_slug_rules(self):
		self.assertRaises(frappe.ValidationError, article, "Bad Slug")
		article("same-slug")
		self.assertRaises(frappe.ValidationError, article, "same-slug")
		article("same-slug", space=OTHER)  # another space may reuse it

	def test_nesting_is_one_level_and_same_space(self):
		parent = article("parent")
		child = article("child", parent_article=parent.name)
		self.assertRaises(frappe.ValidationError, article, "grandchild", parent_article=child.name)
		self.assertRaises(frappe.ValidationError, article, "elsewhere", space=OTHER, parent_article=parent.name)
		self.assertRaises(frappe.ValidationError, frappe.delete_doc, "Doc Article", parent.name)

	def test_published_needs_a_body(self):
		self.assertRaises(frappe.ValidationError, article, "empty", body="")
		article("empty-draft", status="Draft", body="")

	def test_feature_linked_by_published_article_cannot_be_deleted(self):
		frappe.get_doc({"doctype": "Product Feature", "title": "Zz feature", "slug": "zz-feature",
		                "category": "Builder", "status": "Live"}).insert(ignore_permissions=True)
		article("uses-feature", features=[{"feature": "zz-feature"}])
		self.assertRaises(frappe.ValidationError, frappe.delete_doc, "Product Feature", "zz-feature")

	# ── what visitors see ─────────────────────────────────────────────────

	def test_guest_sees_published_only(self):
		article("visible")
		article("hidden", status="Draft")
		article("in-unpublished-space", space=OTHER)
		frappe.set_user("Guest")
		self.assertEqual(api.page_context("%s/visible" % SPACE)["view"], "article")
		self.assertIsNone(api.page_context("%s/hidden" % SPACE))
		self.assertIsNone(api.page_context("%s/in-unpublished-space" % OTHER))
		slugs = [i["slug"] for g in api.get_sidebar(SPACE) for i in g["items"]]
		self.assertIn("visible", slugs)
		self.assertNotIn("hidden", slugs)
		self.assertRaises(frappe.PermissionError, api.save_article, {"title": "x"})

	def test_editor_sees_drafts(self):
		article("draft-for-editor", status="Draft")
		ctx = api.page_context("%s/draft-for-editor" % SPACE)
		self.assertEqual(ctx["article"]["status"], "Draft")

	def test_space_root_redirects_to_its_first_article(self):
		article("first", sort_order=-100)
		article("second", sort_order=-99)
		ctx = api.page_context(SPACE)
		self.assertEqual(ctx["view"], "redirect")
		self.assertEqual(ctx["location"], "/docs/%s/first" % SPACE)

	def test_prev_next_follow_sidebar_order(self):
		article("a-one", sort_order=1)
		article("a-two", sort_order=2)
		article("a-three", sort_order=3)
		art = api.get_article(SPACE, "a-two")
		self.assertEqual(art["prev"]["route"], "/docs/%s/a-one" % SPACE)
		self.assertEqual(art["next"]["route"], "/docs/%s/a-three" % SPACE)

	def test_search_ranks_title_matches_first(self):
		article("zebra-crossing", body="Nothing here.")
		article("other-thing", body="Mentions zebra in passing.")
		results = api.search("zebra", SPACE)
		self.assertEqual([r["slug"] for r in results][:2], ["zebra-crossing", "other-thing"])
		self.assertEqual(api.search("z"), [])  # too short


class TestSiteOwnerGuide(FrappeTestCase):
	"""OPS-08: the guide's files and the seed list agree, and its links stay inside it."""

	def test_every_listed_article_has_a_file_title_and_summary(self):
		import os
		from go1_cms.docs import seed

		for _group, items in seed.GUIDE_ARTICLES:
			for slug, _title in items:
				self.assertTrue(os.path.exists(os.path.join(seed.CONTENT, "guide", slug + ".md")), slug)
				body, summary = seed._read_cms_article(slug, "guide")
				self.assertTrue(summary, slug + " needs a lead paragraph")
				self.assertTrue(body.strip(), slug)

	def test_relative_links_point_at_guide_articles(self):
		import os
		import re
		from go1_cms.docs import seed

		slugs = {s for _g, items in seed.GUIDE_ARTICLES for s, _t in items}
		for slug in slugs:
			body, _ = seed._read_cms_article(slug, "guide")
			for target in re.findall(r"\]\(\.\./([a-z0-9-]+)\)", body):
				self.assertIn(target, slugs, "%s links to a missing article %s" % (slug, target))
		# no stray files that the seed would never load
		files = {f[:-3] for f in os.listdir(os.path.join(seed.CONTENT, "guide")) if f.endswith(".md")}
		self.assertEqual(files, slugs)
