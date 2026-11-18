"""The go1_cms tests.

Run them as the community edition, with every hook of an installed SaaS layer (go1_saas) switched off, to prove go1_cms does not
depend on it:

    CMS_COMMUNITY_EDITION=1 bench --site <site> run-tests --module go1_cms.go1_cms.tests.<module>
"""

import os

if os.environ.get("CMS_COMMUNITY_EDITION"):
	import frappe

	_SAAS = ("go1_saas.", "go1_agent.", "go1_cpanel.")
	_get_hooks = frappe.get_hooks

	def _without_saas(value):
		if isinstance(value, str):
			return None if value.startswith(_SAAS) else value
		if isinstance(value, (list, tuple)):
			return [v for v in (_without_saas(x) for x in value) if v is not None]
		if isinstance(value, dict):
			return type(value)({k: v for k, v in ((k, _without_saas(v)) for k, v in value.items()) if v not in (None, [], {})})
		return value

	def get_hooks(hook=None, default=None, app_name=None):
		out = _without_saas(_get_hooks(hook, default, app_name))
		return default if out is None and default is not None else out if out is not None else ([] if hook else {})

	frappe.get_hooks = get_hooks
