app_name = "dt_recomendations"
app_title = "Dt Recomendations"
app_publisher = "NDF Tech Labs"
app_description = "Creating product groups based on user interactions"
app_email = "info@ndftechlabs.com"
app_license = "agpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "dt_recomendations",
# 		"logo": "/assets/dt_recomendations/logo.png",
# 		"title": "Dt Recomendations",
# 		"route": "/dt_recomendations",
# 		"has_permission": "dt_recomendations.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/dt_recomendations/css/dt_recomendations.css"
# app_include_js = "/assets/dt_recomendations/js/dt_recomendations.js"

# include js, css files in header of web template
# web_include_css = "/assets/dt_recomendations/css/dt_recomendations.css"
# web_include_js = "/assets/dt_recomendations/js/dt_recomendations.js"
web_include_js = ["/assets/dt_recomendations/js/homepage.js"]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dt_recomendations/public/scss/website"

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

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "dt_recomendations/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "dt_recomendations.utils.jinja_methods",
# 	"filters": "dt_recomendations.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "dt_recomendations.install.before_install"
# after_install = "dt_recomendations.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "dt_recomendations.uninstall.before_uninstall"
# after_uninstall = "dt_recomendations.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "dt_recomendations.utils.before_app_install"
# after_app_install = "dt_recomendations.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "dt_recomendations.utils.before_app_uninstall"
# after_app_uninstall = "dt_recomendations.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dt_recomendations.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "Sales Invoice": {
        "on_submit": "dt_recomendations.events.purchase.on_invoice_submit"
    },
    "Payment Entry": {
        "on_submit": "dt_recomendations.events.purchase.on_payment_submit"
    },
    "POS Invoice": {
        "on_submit": "dt_recomendations.events.purchase.on_pos_invoice"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"dt_recomendations.tasks.all"
# 	],
# 	"daily": [
# 		"dt_recomendations.tasks.daily"
# 	],
# 	"hourly": [
# 		"dt_recomendations.tasks.hourly"
# 	],
# 	"weekly": [
# 		"dt_recomendations.tasks.weekly"
# 	],
# 	"monthly": [
# 		"dt_recomendations.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "dt_recomendations.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "dt_recomendations.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "dt_recomendations.event.get_events"
# }

override_whitelisted_methods = {
    "webshop.webshop.doctype.wishlist.wishlist.add_to_wishlist":
    "dt_recomendations.api.add_to_wishlist"
}

override_doctype_class = {
    "Website Item": "dt_recomendations.overrides.website_item.CustomWebsiteItem"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "dt_recomendations.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["dt_recomendations.utils.before_request"]
# after_request = ["dt_recomendations.utils.after_request"]

# Job Events
# ----------
# before_job = ["dt_recomendations.utils.before_job"]
# after_job = ["dt_recomendations.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"dt_recomendations.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
export_python_type_annotations = True

# Require all whitelisted methods to have type annotations
require_type_annotated_api_methods = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

