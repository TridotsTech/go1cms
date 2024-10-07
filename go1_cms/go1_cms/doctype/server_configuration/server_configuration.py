# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, nowdate, today, encode, get_url, get_datetime, to_timedelta, nowtime
from urllib.parse import urlparse, parse_qsl
import requests, json, pymysql, shlex
from frappe import _
from frappe.frappeclient import FrappeClient
from go1_cms.utils.utils import verify_whitelisted_call, safe_decode, run_queue_method

class ServerConfiguration(Document):
	def validate(self):
		if self.enable:
			if not self.users or len(self.users) == 0:
				frappe.throw(frappe._('Please add domain details'))
			check_active = list(filter(lambda x: x.is_active == 1, self.users))
			if len(check_active) == 0:
				frappe.throw(frappe._('Any one domain must be active'))
			elif len(check_active) > 1:
				frappe.throw(frappe._('Only one domain can be active'))

	def install_wildcard(self, url):
		commands=[]
		data = get_current_domain(url)
		#apt update && apt install dnsutils && apt install dig 
		commands.append("sudo bench setup wildcard-ssl {domain} --email info@valiantsystems.com".format(domain=data))
		frappe.log_error(commands, "commands")
		#frappe.enqueue('go1_cms.utils.utils.run_command', commands=commands, doctype="Site Settings",key=today() + " " + nowtime())
		
def get_current_domain(url):
	try:
		import frappe, os, re, json
		import tldextract
		temp_path = ""
		cur_domain = frappe.local.request.host_url.split('/')[-2:][0]
		info = tldextract.extract(cur_domain)
		subdomain=info.subdomain.split(".")[-1:][0]
		cur_domain = info.domain
		if subdomain and subdomain!="www":
			cur_domain = info.domain+"."+info.suffix
		return cur_domain
	except Exception:
		frappe.log_error(frappe.get_traceback(), "server_configuration.get_current_domain")

#check domain availablity in godaddy
@frappe.whitelist()
def check_domain_availablity(domain="list.com"):
	'''
	https://api.ote-godaddy.com/v1/domains/available?domain=gofisto.com&checkType=FAST&forTransfer=false
	'''
	try:
		settings = frappe.get_single('Server Configuration')
		reg_url = settings.reg_url
		reg_key = settings.get_password(fieldname="reg_key", raise_exception=False)
		reg_secret = settings.get_password(fieldname="reg_secret", raise_exception=False)
		url = reg_url+"/v1/domains/available"
		headers = {"Accept": "application/json", "Authorization":"sso-key "+reg_key+":"+reg_secret} 
		parameters = {"domain": domain,"checkType":"FAST", "forTransfer":False}
		response = requests.post(url=url,params=parameters,headers=headers)
		data = response.json()
		return data
	except Exception:
		frappe.log_error(frappe.get_traceback(), "server_configuration.check_domain_availablity")
	
@frappe.whitelist()
def login_current_user():
	user_details = frappe.get_doc('User', frappe.session.user)
	server_configuration = frappe.get_single('Server Configuration')
	if server_configuration.authentication_url:
		data = json.dumps({
			'email': frappe.session.user,
			'provider': 'frappe'
			})
		params = {
			'data': data,
			'get_user_token': 1,
			'check_user': True
		}
		res = requests.post(server_configuration.authentication_url + '/api/method/go1_cms.go1_cms.api.social_login_customer', params)
		try:
			return res.json()
		except Exception as e:
			frappe.log_error(frappe.get_traceback())
			return {}

def get_connection(url):
	connection = None
	settings = frappe.get_single('Server Configuration')
	if settings.enable:
		domain_user = next((x for x in settings.users if x.web_url == url), None)
		if domain_user:
			pwd = frappe.utils.password.get_decrypted_password("Domain User", domain_user.name, fieldname='password')
			connection = FrappeClient(domain_user.web_url, domain_user.username, pwd)
	return connection

#by siva
@frappe.whitelist()
def execute_shell_commands(doctype, domain=None):
	cout = {"root_password": None, "condition": "FF", "admin_password": "#Admin123#"}
	commands = setup_site(doctype, cout, domain)
	for command in commands:
		frappe.enqueue('go1_cms.go1_cms.doctype.server_configuration.server_configuration.connect_external_bench',
			command=command,
			doctype=doctype,
			domain=domain
		)

@frappe.whitelist()
def connect_external_bench(doctype, command, domain=None):
	import paramiko
	domain_config = frappe.get_single('Server Configuration')
	#if settings.enable:
		#domain_config = next((x for x in settings.users if x.web_url), None)
	#username = getpass.getuser()
	hostname = domain_config.host
	#hostname = domain_config.web_url
	username = domain_config.user_name
	password = domain_config.get_password(fieldname="server_password", raise_exception=False)
	application = domain_config.application_path
	
	# initialize the SSH client
	client = paramiko.SSHClient()
	
	# add to known hosts
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		client.connect(hostname=hostname, username=username, password=password)
		arg =[command]
		command='bench execute --args "{command}" go1_cms.utils.utils.run_queue_method'.format(command=arg)
		command = "cd {application} &&{command}".format(application=application, command=command)
		stdin, stdout, stderr = client.exec_command(command)
		err = stderr.read().decode()
		if err:
			print(err)
	except:
		print("[!] Cannot connect to the SSH Server")
		exit()

def setup_new_site(doctype, domain=None):
	ret = pass_exists(doctype)
	print(ret)
	if ret:
		key = today() + " " + nowtime()
		settings = frappe.get_single('Server Configuration')
		admin_password = "#Admin123#"
		db_host = settings.host
		if ret['admin_password'] and ret['condition'][0] != 'T': admin_password = ret['admin_password']
		root_password = settings.get_password(fieldname="mysql_root_password", raise_exception=False)
		if ret['root_password'] and ret['condition'][1] != 'T': root_password = ret['root_password']
		vry = verify_password(site_name=domain, mysql_password=root_password, db_host=db_host)
		print(vry)
		if vry == "console":
			create_new_site(site_name=domain, domain_name=domain, mysql_password=root_password, admin_password=admin_password, key=key)
			

@frappe.whitelist()
def pass_exists(doctype, docname=''):
	verify_whitelisted_call()
	#return string convention 'TT',<root_password>,<admin_password>
	ret = {'condition':'', 'root_password':'', 'admin_password':''}
	common_site_config_path = 'common_site_config.json'
	with open(common_site_config_path, 'r') as f:
		common_site_config_data = json.load(f)

	ret['condition'] += 'T' if common_site_config_data.get('root_password') else 'F'
	ret['root_password'] = common_site_config_data.get('root_password')

	ret['condition'] += 'T' if common_site_config_data.get('admin_password') else 'F'
	ret['admin_password'] = common_site_config_data.get('admin_password')

	if docname == '': #Prompt reached here on new-site
		return ret

	site_config_path = docname+'/site_config.json'
	with open(site_config_path, 'r') as f:
		site_config_data = json.load(f)
	#FF FT TF
	if ret['condition'][1] == 'F':
		ret['condition'] = ret['condition'][0] + 'T' if site_config_data.get('admin_password') else 'F'
		ret['admin_password'] = site_config_data.get('admin_password')
	else:
		if site_config_data.get('admin_password'):
			ret['condition'] = ret['condition'][0] + 'T'
			ret['admin_password'] = site_config_data.get('admin_password')
	return ret

@frappe.whitelist()
def verify_password(site_name, mysql_password, db_host=None):
	verify_whitelisted_call()
	try:
		#if not db_host: db_host= frappe.conf.db_host
		db = pymysql.connect(host=frappe.conf.db_host or 'localhost', user='root' ,passwd=mysql_password)
		db.close()
	except Exception as e:
		print (e)
		frappe.throw("MySQL password is incorrect")
	return "console"

@frappe.whitelist()
def create_new_site(site_name, domain_name, mysql_password, admin_password, key):
	verify_whitelisted_call()
	settings = frappe.get_single('Server Configuration')
	commands = ["bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} {site_name}".format(site_name=site_name,
		admin_password=admin_password, mysql_password=mysql_password)]
	if settings.install_apps == True and settings.app_list:
		with open('apps.txt', 'r') as f:
			available_app_list = f.read()
		app_list = settings.app_list.split("\n")
		
		for app in app_list:
			if app not in available_app_list:
				commands.append("bench get-app {app}".format(app=app))
			commands.append("bench --site {site_name} install-app {app}".format(site_name=site_name, app=app))
		
		commands.append("bench setup add-domain {custom_domain} --site {site_name}".format(custom_domain=domain_name, site_name=site_name))
		commands.append("bench setup nginx --yes")		
		commands.append("bench setup reload-nginx")
	
	frappe.enqueue('go1_cms.utils.utils.run_command',
		commands=commands,
		doctype="Site Settings",
		key=key
	)
	command=["sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=domain_name)]
	#enable ssl domain 
	frappe.enqueue('go1_cms.utils.utils.run_ssl_command',commands=command,doctype="Website",key=today() + " " + nowtime())

def setup_site(doctype, ret, domain_name=None):
	if ret:
		site_name=domain_name
		frappe.log_error(ret)
		key = today() + " " + nowtime()
		settings = frappe.get_single('Server Configuration')
		admin_password = "#Admin123#"
		db_host = settings.host
		if ret['admin_password'] and ret['condition'][0] != 'T': admin_password = ret['admin_password']
		mysql_password = settings.get_password(fieldname="mysql_root_password", raise_exception=False)
		if ret['root_password'] and ret['condition'][1] != 'T': mysql_password = ret['root_password']
		try:
			#if not db_host: db_host= frappe.conf.db_host
			db = pymysql.connect(host=frappe.conf.db_host or 'localhost', user='root' ,passwd=mysql_password)
			db.close()
		except Exception as e:
			frappe.log_error(e)
			frappe.throw("MySQL password is incorrect")
		vry = "console"
		if vry == "console":
			settings = frappe.get_single('Server Configuration')
			commands = ["bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} {site_name}".format(site_name=site_name,
				admin_password=admin_password, mysql_password=mysql_password)]
			if settings.install_apps == True and settings.app_list:
				with open('apps.txt', 'r') as f:
					available_app_list = f.read()
				app_list = settings.app_list.split("\n")
		
				for app in app_list:
					if app not in available_app_list:
						commands.append("bench get-app {app}".format(app=app))
					commands.append("bench --site {site_name} install-app {app}".format(site_name=site_name, app=app))
		
				commands.append("bench setup add-domain {custom_domain} --site {site_name}".format(custom_domain=domain_name, site_name=site_name))
				commands.append("bench setup nginx --yes")		
				commands.append("bench setup reload-nginx")
			commands.append("sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=domain_name))
			return commands

