# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import googleapiclient.discovery
import google.oauth2.credentials

from frappe import _
from googleapiclient.errors import HttpError
from frappe.utils import get_request_site_address
from six.moves.urllib.parse import quote
from frappe.integrations.doctype.google_settings.google_settings import get_auth_url
from go1_cms.utils.setup import get_theme_settings


SCOPES = "https://www.googleapis.com/auth/indexing"


@frappe.whitelist()
def authorize_access(reauthorize=None):
	"""If no Authorization code get it from Google and then request for Refresh Token."""

	
	website_settings = None
	website_settings = get_theme_settings()
	if not website_settings:
		website_settings = frappe.get_doc("Website Settings")
		google_settings = frappe.get_doc("Google Settings")
	else:
		
		website_settings = frappe.get_doc("Web Theme", website_settings)
		google_settings = frappe.get_doc("Web Theme", website_settings.name)
	redirect_uri = get_request_site_address(True) + "?cmd=go1_cms.utils.google_indexing.google_callback"
	
	if not website_settings.indexing_authorization_code or reauthorize:
		return get_authentication_url(client_id=google_settings.client_id, redirect_uri=redirect_uri)
	else:
		try:
			data = {
				"code": website_settings.indexing_authorization_code,
				"client_id": google_settings.client_id,
				"client_secret": google_settings.get_password(fieldname="client_secret", raise_exception=False),
				"redirect_uri": redirect_uri,
				"grant_type": "authorization_code"
			}
			res = requests.post(get_auth_url(), data=data).json()

			if "refresh_token" in res:
				frappe.db.set_value("Web Theme", website_settings.name, "indexing_refresh_token", res.get("refresh_token"))
				# frappe.db.set_value("Website Settings", website_settings.name, "indexing_refresh_token", res.get("refresh_token"))
				frappe.db.commit()

			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = "/desk#Form/{0}/{1}".format(quote("Web Theme"), website_settings.name)
			# frappe.local.response["location"] = "/desk#Form/{0}".format(quote("Website Settings"))

			frappe.msgprint(_("Google Indexing has been configured."))
		except Exception as e:
			frappe.throw(e)


def get_authentication_url(client_id, redirect_uri):
	"""Return authentication url with the client id and redirect uri."""
	return {
		"url": "https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&response_type=code&prompt=consent&client_id={}&include_granted_scopes=true&scope={}&redirect_uri={}".format(client_id, SCOPES, redirect_uri)
	}


@frappe.whitelist()
def google_callback(code=None):
	try:
		"""Authorization code is sent to callback as per the API configuration."""
		website_settings = get_theme_settings()
		frappe.db.set_value("Web Theme", website_settings, "indexing_authorization_code", code)
		# frappe.db.set_value("Website Settings", None, "indexing_authorization_code", code)
		frappe.db.commit()

		authorize_access()
	except Exception as e:
		frappe.throw(e)


def get_google_indexing_object():
	try:
		from google_indexing.google_indexing.docevents import get_access_token
		"""Returns an object of Google Indexing object."""
		account = None
		account = get_theme_settings()
		if not account:
			account = frappe.get_doc("Website Settings")
			google_settings = frappe.get_doc("Google Settings")
		else:
			account = frappe.get_doc("Web Theme", account)
			google_settings = frappe.get_doc("Web Theme", account.name)

		credentials_dict = {
			"token": get_access_token(doc=account),
			"refresh_token": account.get_password(fieldname="indexing_refresh_token", raise_exception=False),
			"token_uri": get_auth_url(),
			"client_id": google_settings.client_id,
			"client_secret": google_settings.get_password(fieldname="client_secret", raise_exception=False),
			"scopes": "https://www.googleapis.com/auth/indexing"
		}
		credentials = google.oauth2.credentials.Credentials(**credentials_dict)
		google_indexing = googleapiclient.discovery.build("indexing", "v3", credentials=credentials)

		return google_indexing
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.get_google_indexing_object.get_google_indexing_object')

@frappe.whitelist()
def publish_site(url, operation_type="URL_UPDATED"):
	try:
		"""Send an update/remove url request."""
		google_indexing = get_google_indexing_object()
		body = {
			"url": url,
			"type": operation_type
		}
		try:
			google_indexing.urlNotifications().publish(body=body, x__xgafv='2').execute()
		except HttpError as e:
			frappe.log_error(message=e, title='API Indexing Issue')
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.get_google_indexing_object.publish_site')



@frappe.whitelist(allow_guest=True)
def make_view_log(path, referrer=None, browser=None, version=None, url=None, user_tz=None):
	try:
		if not is_tracking_enabled():
			return

		request_dict = frappe.request.__dict__
		user_agent = request_dict.get('environ', {}).get('HTTP_USER_AGENT')

		if referrer:
			referrer = referrer.split('?')[0]

		is_unique = True
		if referrer.startswith(url):
			is_unique = False

		if path != "/" and path.startswith('/'):
			path = path[1:]

		view = frappe.new_doc("Web Page View")
		view.path = path
		view.referrer = referrer
		view.browser = browser
		view.browser_version = version
		view.time_zone = user_tz
		view.user_agent = user_agent
		view.is_unique = is_unique

		try:
			view.insert(ignore_permissions=True)
		except Exception:
			if frappe.message_log:
				frappe.message_log.pop()
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.get_google_indexing_object.make_view_log')


@frappe.whitelist()
def get_page_view_count(path):
	return frappe.db.count("Web Page View", filters={'path': path})

def is_tracking_enabled():
	try:
		settings = get_theme_settings()
		settings = frappe.get_doc("Web Theme", settings)
		if hasattr(settings, 'enable_view_tracking'):
			return settings.get('enable_view_tracking')
		return frappe.db.get_value("Website Settings", "Website Settings", "enable_view_tracking")
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.get_google_indexing_object.is_tracking_enabled')

@frappe.whitelist()
def create_google_project():
	url = "https://console.developers.google.com/projectcreate"
	data = {"project_id": "gokommerce123", "projectId":"Gokommerce"}
	response = requests.post(url, data=data)
	return response

@frappe.whitelist()
def get_google_project():
	url = "https://cloudresourcemanager.googleapis.com/v1/projects/gokommerce123"
	response = requests.post(url).json()
	return response

@frappe.whitelist()
def create_google_projects():
	from googleapiclient import discovery
	from oauth2client.client import GoogleCredentials
	credentials = GoogleCredentials.get_application_default()
	service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
	project_body = {
		"projectId": "gokommerce",
	  	"projectNumber": 10}
	request = service.projects().create(body=project_body)
	response = request.execute()
	return response

@frappe.whitelist()
def update_bulk_apiindexing(operation_type='URL_UPDATED'):
	try:
		"""Send indexing request on update/trash operation."""
		routes = {}
		doctypes_with_web_view = [d.name for d in frappe.db.get_all('DocType', {
			'has_web_view': 1
		})]
		from frappe.model.document import get_controller
		for doctype in doctypes_with_web_view:
			controller = get_controller(doctype)
			meta = frappe.get_meta(doctype)
			condition_field = meta.is_published_field or controller.website.condition_field
			filters={condition_field: 1}
			res = frappe.db.get_all(doctype, ['route', 'name', 'modified'], filters)
			for r in res:
				from go1_cms.utils.setup import get_theme_settings
				website_settings = get_theme_settings()
				if frappe.db.get_value("Web Theme", website_settings, "enable_google_indexing"):
					url = frappe.utils.get_url(r.route)
					frappe.enqueue('google_indexing.google_indexing.google_indexing.publish_site', \
						url=url, operation_type=operation_type)
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.go1_cms.setup.send_indexing_request')
