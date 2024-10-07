#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import frappe, json, requests, os, re, time, socket, getpass
from frappe import _
from frappe.utils import cstr, flt, getdate, nowdate, today, encode, get_url, get_datetime, to_timedelta
from datetime import date, datetime, timedelta
from frappe.core.doctype.domain_settings.domain_settings import get_active_domains
from six import iteritems, text_type, string_types
import re, shlex
from subprocess import check_output, Popen, PIPE, STDOUT
from go1_cms.utils.utils import verify_whitelisted_call, safe_decode, _close_the_doc

@frappe.whitelist(allow_guest=True)
def setup_nginx(domain=None):
	try:
		'''domain mapping and enable ssl '''
		print("----------------setup-nginx-------------------")
		if not domain:
			domain ="test.gokommerce.com"
		input0 = "#godabao123#"
		console_dump = ""
		console_dumps=""
		dateTimeObj = datetime.now()
		start_time = frappe.utils.time.time()
		from frappe.utils import cstr
		site_name = cstr(frappe.local.site)
		key = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S.%f")
		server_username = getpass.getuser()
	
		terminal = Popen(shlex.split("sudo bench setup add-domain {alias}".format(alias=domain)), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd="..")
		for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
			frappe.publish_realtime(key, c, user=frappe.session.user)
			console_dump += c
		input1 = site_name+"\n"
		concat_query0 = "{}\n".format(input1)
		terminal.communicate(input=concat_query0.encode('utf-8'))
		#terminal.stdin.close()
		if terminal.wait():
			_close_the_doc(start_time, key, console_dump, status='Failed', user=frappe.session.user)
		else:
			_close_the_doc(start_time, key, console_dump, status='Success', user=frappe.session.user)
		
		nginx = Popen(shlex.split("sudo bench setup production {servername}".format(servername=server_username)), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd="..")
		for c in iter(lambda: safe_decode(nginx.stdout.read(1)), ''):
			frappe.publish_realtime(key, c, user=frappe.session.user)
			console_dumps += c		
		input2 = "y"
		input3 = "y"
		concat_query = "{}\n{}\n".format(input2, input3)
		nginx.communicate(input=concat_query.encode('utf-8'))
		#nginx.stdin.close()
		if nginx.wait():
			_close_the_doc(start_time, key, console_dumps, status='Failed', user=frappe.session.user)
		else:
			_close_the_doc(start_time, key, console_dumps, status='Success', user=frappe.session.user)
		return {"state":"success"}
	except Exception:
		frappe.log_error(frappe.get_traceback(),'go1_cms.utils.domain_setup.setup_nginx')


