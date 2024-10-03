from . import __version__ as app_version

app_name = "go1_cms"
app_title = "Go1 CMS"
app_publisher = "Tridotstech"
app_description = "Go1 CMS"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@tridotstech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/go1_cms/css/cms.css"
app_include_js = "/assets/go1_cms/js/cms.js"


update_website_context = [
    "go1_cms.go1_cms.api.update_website_context",
]

on_logout = "go1_cms.api.utils.clear_cookie_cart"

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

# doctype_js = {
#     "Job Opening": "templates/controllers/js/job_opening.js"
# }

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

website_route_rules = [
    {"from_route": "/cms/<path:app_path>", "to_route": "cms"},
]

email_css = ["/assets/go1_cms/email/email.css"]

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# before_install = "go1_cms.install.before_install"
# after_install = "go1_cms.install.after_install"
after_install = "go1_cms.go1_cms.after_install.after_install"

# Uninstallation
# before_uninstall = "go1_cms.uninstall.before_uninstall"
# after_uninstall = "go1_cms.uninstall.after_uninstall"
before_uninstall = "go1_cms.go1_cms.before_uninstall.before_uninstall"

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

override_doctype_class = {
    "Job Opening": "go1_cms.overrides.job_opening.CustomJobOpening",
    "Website Item": "go1_cms.overrides.website_item.CustomWebsiteItem",
}

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
        "on_update": "go1_cms.go1_cms.api.update_web_themes",
    },
    "Color Palette": {
        "on_update": "go1_cms.go1_cms.api.update_web_themes",
    },
    # "Job Opening": {
    #     "validate": "go1_cms.go1_cms.api.insert_job_opening_website"
    # }
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

scheduler_events = {
    "daily": [
        "go1_cms.scheduled_tasks.delete_old_captcha"
    ],
}

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

# fixtures = [
#     {"doctype": "Custom Field", "filters": [{"module": "Go1 CMS"}]},
# ]
