# -*- coding: utf-8 -*-
# Copyright (c) 2017, Tridots Tech Private Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from subprocess import Popen, PIPE, STDOUT
import re, shlex
from frappe.utils import cstr, flt, getdate, nowdate, today, encode, get_url, get_datetime, to_timedelta, nowtime
from six import iteritems, text_type, string_types

def run_command(commands, doctype, key, cwd='..', docname=None, after_command=None):

	start_time = frappe.utils.time.time()
	frappe.log_error("start_time", start_time)
	console_dump = ""
	logged_command = " && ".join(commands)
	logged_command += " " #to make sure passwords at the end of the commands are also hidden
	sensitive_data = ["--mariadb-root-password", "--admin-password", "--root-password"]
	for password in sensitive_data:
		logged_command = re.sub("{password} .*? ".format(password=password), '', logged_command, flags=re.DOTALL)
	frappe.log_error("logged_command", logged_command)
	doc = frappe.get_doc({'doctype': 'Executed Command', 'key': key, 'source': doctype+': '+docname,
		'command': logged_command, 'console': console_dump, 'status': 'Ongoing'})
	doc.insert()
	frappe.db.commit()
	frappe.publish_realtime(key, "Executing Command:\n{logged_command}\n\n".format(logged_command=logged_command), user=frappe.session.user)
	try:
		frappe.log_error("commands", commands)
		for command in commands:
			terminal = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
			frappe.log_error("terminal", terminal)
			for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
				frappe.publish_realtime(key, c, user=frappe.session.user)
				console_dump += c
		if terminal.wait():
			_close_the_doc(start_time, key, console_dump, status='Failed', user=frappe.session.user)
		else:
			_close_the_doc(start_time, key, console_dump, status='Success', user=frappe.session.user)
	except Exception as e:
		_close_the_doc(start_time, key, "{} \n\n{}".format(e, console_dump), status='Failed', user=frappe.session.user)
	finally:
		frappe.db.commit()
		# hack: frappe.db.commit() to make sure the log created is robust,
		# and the _refresh throws an error if the doc is deleted 
		frappe.enqueue('go1_cms.utils.utils._refresh',
			doctype=doctype, docname=docname, commands=commands)

def run_ssl_command(commands, doctype, key, cwd='..', docname=None, after_command=None):
	start_time = frappe.utils.time.time()
	console_dump = ""
	logged_command = " && ".join(commands)
	logged_command += " " #to make sure passwords at the end of the commands are also hidden
	sensitive_data = ["--mariadb-root-password", "--admin-password", "--root-password"]
	for password in sensitive_data:
		logged_command = re.sub("{password} .*? ".format(password=password), '', logged_command, flags=re.DOTALL)
	doc = frappe.get_doc({'doctype': 'Executed Command', 'key': key, 'source': doctype+': '+docname,
		'command': logged_command, 'console': console_dump, 'status': 'Ongoing'})
	doc.insert()
	frappe.db.commit()
	frappe.publish_realtime(key, "Executing Command:\n{logged_command}\n\n".format(logged_command=logged_command), user=frappe.session.user)
	try:
		for command in commands:
			terminal = Popen(shlex.split(command), stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=cwd)
			input2 = "Y"
			input3 = "Y"
			concat_query = "{}\n{}\n".format(input2, input3)
			terminal.communicate(input=concat_query.encode('utf-8'))
			for c in iter(lambda: safe_decode(terminal.stdout.read(1)), ''):
				frappe.publish_realtime(key, c, user=frappe.session.user)
				console_dump += c
		if terminal.wait():
			_close_the_doc(start_time, key, console_dump, status='Failed', user=frappe.session.user)
		else:
			_close_the_doc(start_time, key, console_dump, status='Success', user=frappe.session.user)
	except Exception as e:
		_close_the_doc(start_time, key, "{} \n\n{}".format(e, console_dump), status='Failed', user=frappe.session.user)
	finally:
		frappe.db.commit()
		# hack: frappe.db.commit() to make sure the log created is robust,
		# and the _refresh throws an error if the doc is deleted 
		frappe.enqueue('go1_cms.utils.utils._refresh',
			doctype=doctype, docname=docname, commands=commands)

def _close_the_doc(start_time, key, console_dump, status, user):
	time_taken = frappe.utils.time.time() - start_time
	final_console_dump = ''
	console_dump = console_dump.split('\n\r')
	for i in console_dump:
		i = i.split('\r')
		final_console_dump += '\n'+i[-1]
	frappe.set_value('Executed Command', key, 'console', final_console_dump)
	frappe.set_value('Executed Command', key, 'status', status)
	frappe.set_value('Executed Command', key, 'time_taken', time_taken)
	frappe.publish_realtime(key, '\n\n'+status+'!\nThe operation took '+str(time_taken)+' seconds', user=user)

def _refresh(doctype, docname, commands):
	frappe.get_doc(doctype, docname).run_method('after_command', commands=commands)

@frappe.whitelist()
def verify_whitelisted_call():
	if 'go1_cms' not in frappe.get_installed_apps():
		raise ValueError("This site does not have Ecommerce Business Store installed.")

def safe_decode(string, encoding = 'utf-8'):
	try:
		string = string.decode(encoding)
	except Exception:
		pass
	return string

@frappe.whitelist()
def run_queue_method(command):
	commands=[]
	if command:
		commands.append(command)
	key = today() + " " + nowtime()
	frappe.enqueue('go1_cms.utils.utils.run_command',
		commands=commands,
		doctype="Site Settings",
		key=key
	)
