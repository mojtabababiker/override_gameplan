app_name = "override_gameplan"
app_title = "Override Gameplan"
app_publisher = "Mojtaba Babiker"
app_description = "App that adds custom functionalities and features for the Gameplan app tailored to breakpoint"
app_email = "mojtabababiker.dev@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "override_gameplan",
# 		"logo": "/assets/override_gameplan/logo.png",
# 		"title": "Override Gameplan",
# 		"route": "/override_gameplan",
# 		"has_permission": "override_gameplan.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/override_gameplan/css/override_gameplan.css"
# app_include_js = "/assets/override_gameplan/js/override_gameplan.js"

# include js, css files in header of web template
# web_include_css = "/assets/override_gameplan/css/override_gameplan.css"
# web_include_js = "/assets/override_gameplan/js/override_gameplan.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "override_gameplan/public/scss/website"

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
# app_include_icons = "override_gameplan/public/icons.svg"

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
# 	"methods": "override_gameplan.utils.jinja_methods",
# 	"filters": "override_gameplan.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "override_gameplan.install.before_install"
# after_install = "override_gameplan.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "override_gameplan.uninstall.before_uninstall"
# after_uninstall = "override_gameplan.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "override_gameplan.utils.before_app_install"
# after_app_install = "override_gameplan.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "override_gameplan.utils.before_app_uninstall"
# after_app_uninstall = "override_gameplan.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "override_gameplan.notifications.get_notification_config"

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

doc_events = {
    "User": {
        "after_insert": "override-gameplan.sync-hooks.user_profile.create_user_profile",
        "on_update": "override-gameplan.sync-hooks.user_profile.on_user_update",
    },
    "ToDo": {
        "after_insert": "override-gameplan.sync-hooks.todo.handle_assignment.handle_assignment",
        "on_update": "override-gameplan.sync-hooks.todo.handle_assignment.handle_assignment_removal",
    },
    "Customer": {
        "after_insert": "override-gameplan.sync-hooks.team.create_team",
        "on_update": "override-gameplan.sync-hooks.team.on_customer_update",
        "on_trash": "override-gameplan.sync-hooks.team.on_customer_trash",
    },
    "Project": {
        "after_insert": "override-gameplan.sync-hooks.project.create_project",
        "on_update": "override-gameplan.sync-hooks.project.on_project_update",
        "on_trash": "override-gameplan.sync-hooks.project.on_project_trash",
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"override_gameplan.tasks.all"
# 	],
# 	"daily": [
# 		"override_gameplan.tasks.daily"
# 	],
# 	"hourly": [
# 		"override_gameplan.tasks.hourly"
# 	],
# 	"weekly": [
# 		"override_gameplan.tasks.weekly"
# 	],
# 	"monthly": [
# 		"override_gameplan.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "override_gameplan.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "override_gameplan.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "override_gameplan.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "override_gameplan.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["override_gameplan.utils.before_request"]
# after_request = ["override_gameplan.utils.after_request"]

# Job Events
# ----------
# before_job = ["override_gameplan.utils.before_job"]
# after_job = ["override_gameplan.utils.after_job"]

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
# 	"override_gameplan.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
