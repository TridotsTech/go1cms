"""Shared fixtures for the main CMS tests (OPS-09).

Everything is created inside the test transaction and rolled back by
FrappeTestCase, so nothing lands on the site. Names carry a "zz-ops09" prefix so
a stray row is easy to spot.

    bench --site <site> run-tests --app go1_cms
"""

import json

import frappe

DOCTYPE = "Web Page Builder"


def layout(*texts):
	"""A tiny valid page layout with one text node per string."""
	return json.dumps({"sections": [
		{"id": "s%d" % i, "type": "section", "children": [{"id": "t%d" % i, "type": "text", "content": t}]}
		for i, t in enumerate(texts)
	]})


def make_user(email, *roles):
	if frappe.db.exists("User", email):
		frappe.delete_doc("User", email, force=True, ignore_permissions=True)
	user = frappe.get_doc({"doctype": "User", "email": email, "first_name": email.split("@")[0],
	                       "send_welcome_email": 0, "enabled": 1})
	for role in roles:
		user.append("roles", {"role": role})
	user.insert(ignore_permissions=True)
	return user


def make_project(name, slug, member=None):
	doc = frappe.get_doc({"doctype": "CMS Project", "project_name": name, "project_slug": slug, "status": "Draft"})
	if member:
		doc.append("members", {"user": member, "access": "Owner"})
	doc.insert(ignore_permissions=True)
	return doc.name


def make_page(title, route, project=None, draft=None, live=None, published=0):
	doc = frappe.get_doc({
		"doctype": DOCTYPE, "page_title": title, "route": route, "use_page_builder": 1,
		"project": project, "draft_layout_json": draft or "", "layout_json": live or "", "published": published,
	})
	doc.insert(ignore_permissions=True)
	return doc.name
