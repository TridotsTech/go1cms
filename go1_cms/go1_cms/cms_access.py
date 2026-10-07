"""Who may edit, and which websites (CMS Projects) they may touch.

Every admin service that changes pages, themes or projects calls one of these first.

- Editors are System Managers, Website Managers and Panel Customers.
- System Managers (and Administrator) see every project.
- Everyone else sees only the projects they are a member of (CMS Project > Members),
  plus any project a Panel Customer holds a User Permission for.
- A page with no project is visible to System Managers only.
"""

import frappe
from frappe import _

EDITOR_ROLES = {"System Manager", "Website Manager", "Panel Customer"}


def _user(user=None):
	return user or frappe.session.user


def sees_all_projects(user=None):
	user = _user(user)
	return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def is_editor(user=None):
	user = _user(user)
	if not user or user == "Guest":
		return False
	return user == "Administrator" or bool(set(frappe.get_roles(user)) & EDITOR_ROLES)


def deny(message=None):
	frappe.throw(message or _("You do not have permission to do this."), frappe.PermissionError)


def require_editor():
	if not is_editor():
		deny(_("You need editing rights for this."))


def require_system_manager():
	if not sees_all_projects():
		deny()


def allowed_projects(user=None):
	"""Project names the user may open, or None for every project."""
	user = _user(user)
	if sees_all_projects(user):
		return None
	members = frappe.get_all(
		"CMS Project Member",
		filters={"user": user, "parenttype": "CMS Project", "parentfield": "members"},
		pluck="parent",
		ignore_permissions=True,
	)
	granted = frappe.get_all(
		"User Permission", filters={"user": user, "allow": "CMS Project"}, pluck="for_value", ignore_permissions=True
	)
	return sorted(set(members) | set(granted))


def can_access_project(project, user=None):
	allowed = allowed_projects(user)
	if allowed is None:
		return True
	return bool(project) and project in allowed


def require_project(project):
	require_editor()
	if not can_access_project(project):
		deny(_("You do not have access to this website."))


def require_page(page_name, doctype="Web Page Builder"):
	"""The page must exist and belong to a project the user may open."""
	require_editor()
	if sees_all_projects():
		return
	if doctype and doctype != "Web Page Builder":
		return  # shared library records (components, templates) carry no project
	project = frappe.db.get_value("Web Page Builder", page_name, "project")
	if not can_access_project(project):
		deny(_("You do not have access to this page."))


def require_page_route(route):
	require_editor()
	if sees_all_projects():
		return
	route = (route or "").strip("/")
	name = frappe.db.get_value("Web Page Builder", {"route": route}, "name") or frappe.db.get_value(
		"Web Page Builder", {"route": "/" + route}, "name"
	)
	if not name:
		deny(_("You do not have access to this page."))
	require_page(name)


def is_project_owner(project, user=None):
	user = _user(user)
	if sees_all_projects(user):
		return True
	return bool(
		frappe.db.exists(
			"CMS Project Member", {"parent": project, "parenttype": "CMS Project", "user": user, "access": "Owner"}
		)
	)


def add_member(project, user, access="Editor"):
	"""Idempotent; never downgrades an Owner.

	Writes the member row on its own, without re-saving the website: some older
	websites fail today's save checks (Krishko keeps an empty project_slug on
	purpose), and adding a person must not depend on that."""
	row = frappe.db.get_value(
		"CMS Project Member", {"parent": project, "parenttype": "CMS Project", "parentfield": "members", "user": user},
		["name", "access"], as_dict=True,
	)
	if row:
		if access == "Owner" and row.access != "Owner":
			frappe.db.set_value("CMS Project Member", row.name, "access", "Owner", update_modified=False)
		return
	idx = frappe.db.count("CMS Project Member", {"parent": project, "parenttype": "CMS Project"}) + 1
	frappe.get_doc({
		"doctype": "CMS Project Member",
		"parent": project,
		"parenttype": "CMS Project",
		"parentfield": "members",
		"idx": idx,
		"user": user,
		"access": access,
	}).db_insert()


# ── Members dialog (Projects screen) ─────────────────────────────────────────


def _members_out(project):
	rows = frappe.get_all(
		"CMS Project Member",
		filters={"parent": project, "parenttype": "CMS Project"},
		fields=["user", "access"],
		order_by="idx asc",
		ignore_permissions=True,
	)
	names = {
		u.name: u.full_name
		for u in frappe.get_all(
			"User", filters={"name": ["in", [r.user for r in rows] or [""]]}, fields=["name", "full_name"], ignore_permissions=True
		)
	}
	return {
		"project": project,
		"can_manage": is_project_owner(project),
		"members": [{"user": r.user, "full_name": names.get(r.user) or r.user, "access": r.access} for r in rows],
	}


@frappe.whitelist()
def get_project_members(project):
	require_project(project)
	return _members_out(project)


@frappe.whitelist()
def add_project_member(project, user, access="Editor"):
	require_project(project)
	if not is_project_owner(project):
		deny(_("Only the website's owner can change its members."))
	user = (user or "").strip().lower()
	if access not in ("Owner", "Editor"):
		frappe.throw(_("Access must be Owner or Editor."))
	if not frappe.db.exists("User", user) or not frappe.db.get_value("User", user, "enabled"):
		frappe.throw(_("No active account uses {0}. Ask them to sign up first.").format(user))
	if not is_editor(user):
		frappe.throw(_("{0} does not have editing rights on this site.").format(user))
	add_member(project, user, access)
	return _members_out(project)


@frappe.whitelist()
def remove_project_member(project, user):
	require_project(project)
	if not is_project_owner(project):
		deny(_("Only the website's owner can change its members."))
	rows = frappe.get_all(
		"CMS Project Member", filters={"parent": project, "parenttype": "CMS Project"},
		fields=["name", "user", "access"], ignore_permissions=True,
	)
	keep = [r for r in rows if r.user != user]
	if not any(r.access == "Owner" for r in keep) and not sees_all_projects():
		frappe.throw(_("A website needs at least one owner."))
	for r in rows:
		if r.user == user:
			frappe.db.delete("CMS Project Member", {"name": r.name})
	return _members_out(project)


def can_see_draft(page_name, user=None):
	"""Unpublished content is for the page's own editors only (SEC-06) — and for a
	client holding a live review link to this very page (CMT-06, `?review=`)."""
	if not is_editor(user):
		token = (frappe.form_dict or {}).get("review") if user is None else None
		if token:
			try:
				from cms_frontend.review import page_for_token

				return page_for_token(token) == page_name
			except Exception:
				return False
		return False
	if sees_all_projects(user):
		return True
	return can_access_project(frappe.db.get_value("Web Page Builder", page_name, "project"), user)
