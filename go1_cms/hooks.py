from . import __version__ as app_version

app_name = "go1_cms"
app_title = "Go1 CMS"
app_publisher = "Tridotstech"
app_description = "Go1 CMS"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@tridotstech.com"
app_license = "MIT"



# include js, css files in header of desk.html
app_include_css = "/assets/go1_cms/css/cms.css"
app_include_js = "/assets/go1_cms/js/cms.js"




update_website_context = [
	"go1_cms.go1_cms.api.update_website_context",
]

# include js, css files in header of web template
# web_include_css = "/assets/go1_cms/css/go1_cms.css"
# web_include_js = "/assets/go1_cms/js/go1_cms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "go1_cms/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "go1_cms.install.before_install"
# after_install = "go1_cms.install.after_install"
after_install = "go1_cms.go1_cms.after_install.after_install"

# Docs (go1_cms/docs): the Docs Editor role exists before the doctypes that name
# it are synced; a site with no docs yet gets the seeded spaces, articles and
# feature catalogue on its first migrate.
before_migrate = ["go1_cms.docs.setup.ensure_role"]
after_migrate = ["go1_cms.docs.setup.after_migrate", "go1_cms.go1_cms.business.after_migrate"]

# /sitemap.xml (cms_frontend www/sitemap.py): every published docs article and
# showcase page, which own no Web Page Builder row.
cms_sitemap_urls = ["go1_cms.docs.api.sitemap_urls"]
# /docs is the docs site even where an old builder page holds the route "docs".
page_renderer = ["go1_cms.docs.renderer.DocsPageRenderer"]

# Uninstallation
# ------------

# before_uninstall = "go1_cms.uninstall.before_uninstall"
# after_uninstall = "go1_cms.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "go1_cms.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Header Component": {
		"on_update": "go1_cms.go1_cms.api.update_web_themes",
	},
	"Footer Component": {
		"on_update": "go1_cms.go1_cms.api.update_web_themes",
	},
	"Web Page Builder": {
		"on_update": [
			"go1_cms.go1_cms.api.update_web_themes",
			# MNU-02: menu links follow a page whose address changes.
			"go1_cms.go1_cms.menu_api.follow_page_route_change",
			# MNU-03: menus that list pages automatically go stale.
			"go1_cms.go1_cms.menu_api.clear_auto_menus",
		],
		"on_trash": "go1_cms.go1_cms.menu_api.clear_auto_menus",
		"after_rename": "go1_cms.go1_cms.menu_api.clear_auto_menus",
	},
	"Blog Post": {
		"on_update": "go1_cms.go1_cms.menu_api.clear_auto_menus",
		"on_trash": "go1_cms.go1_cms.menu_api.clear_auto_menus",
	},
	"Color Palette": {
		"on_update": "go1_cms.go1_cms.api.update_web_themes",
	},
	# Business: every CMS Project has one, and every row that names a project also
	# names its business (see go1_cms/go1_cms/business.py).
	"CMS Project": {
		"after_insert": "go1_cms.go1_cms.business.on_project_save",
		"on_update": "go1_cms.go1_cms.business.on_project_save",
		"on_trash": "go1_cms.go1_cms.business.on_project_trash",
	},
	"*": {
		"before_save": "go1_cms.go1_cms.business.stamp",
	},

}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"go1_cms.tasks.all"
# 	],
# 	"daily": [
# 		"go1_cms.tasks.daily"
# 	],
# 	"hourly": [
# 		"go1_cms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"go1_cms.tasks.weekly"
# 	]
# 	"monthly": [
# 		"go1_cms.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "go1_cms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "go1_cms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "go1_cms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"go1_cms.auth.validate"
# ]
get_translated_dict = {
	("doctype", "Global Defaults"): "frappe.geo.country_info.get_translated_dict"
}
