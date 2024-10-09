# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt
# By sivaranjani

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from subprocess import Popen, PIPE, STDOUT, check_output
from frappe.utils import cstr, nowtime, getdate, today, date_diff
import os, re, json, time, pymysql, shlex
from datetime import date, datetime, timedelta
from urllib.parse import urlparse
import socket
import getpass
from frappe.query_builder import DocType
from go1_cms.go1_cms.doctype.server_configuration.server_configuration import get_connection, setup_new_site, connect_external_bench, execute_shell_commands

class SiteSettings(Document):
	def validate(self):
		domain_config = frappe.get_single('Server Configuration')
		if domain_config.setup_domain and domain_config.external_server==0:
			#validate A Record
			self.check_subdomain_with_arecord()
		if self.is_domain_verified and not self.domain:
			self.is_domain_verified = 0

	def on_update(self):
		#wildcard_domains = self.get_wildcard_ssl_enabled_domains()
		#print(wildcard_domains)
		domain_config = frappe.get_single('Server Configuration')
		site_name = cstr(frappe.local.site)
		username = getpass.getuser()
		domain_array = self.get_domain_array()
		#setup domain internal bench
		wwwdomain = "www."+self.domain_name
		tmt = today() + " " + nowtime()
		if domain_config.setup_domain and domain_config.external_server==0:
			if self.domain_name not in domain_array:
				# add domain bench setup sync-domains, sudoers or add (sudo visudo && serveruser ALL=(ALL) NOPASSWD: ALL)
				#commands = ["sudo bench setup sudoers {username}".format(username=username)]
				commands = ["bench setup add-domain {custom_domain} --site {site_name}".format(custom_domain=self.domain_name, site_name=site_name)]
				#enable domain with wwww
				if domain_config.enable_www==1 and self.disable_www==0:
					commands.append("bench setup add-domain {custom_domain} --site {site_name}".format(custom_domain=wwwdomain, site_name=site_name))

				# setup nginx config and reloading the nginx service		
				commands.append("bench setup nginx --yes")		
				commands.append("bench setup reload-nginx")
				frappe.enqueue('go1_cms.utils.utils.run_command', commands=commands, doctype="Site Settings",key=today() + " " + nowtime())
				
				#check if not wildcard ssl installed
				if domain_config.installed_wildcard_ssl==0 or (domain_config.installed_wildcard_ssl==1 and self.enable_custom_ssl==1):
					# add custom ssl or lets's encrypt ssl
					command=[]	
					command.append("sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=self.domain_name))
					#enable ssl domain with wwww
					frappe.enqueue('go1_cms.utils.utils.run_ssl_command',commands=command,doctype="Site Settings",key=today() + " " + nowtime())
					if domain_config.enable_www==1 and self.disable_www==0:
						wwwcommand=["sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=wwwdomain)]
						frappe.enqueue('go1_cms.utils.utils.run_ssl_command',commands=wwwcommand,doctype="Site Settings",key=today() + " " + nowtime())
			else:
				#install ssl 
				self.enable_only_ssl()
				
		#check nginx state, if error exist roleback
		if domain_config.setup_domain:
			frappe.enqueue('go1_cms.go1_cms.doctype.site_settings.site_settings.process_for_nginx',name=self.name)

		#setup domain external bench
		if domain_config.setup_domain and domain_config.external_server==1:
			self.connect_external_bench()

	def enable_only_ssl(self):
		#check if not wildcard ssl installed
		domain_config = frappe.get_single('Server Configuration')
		site_name = cstr(frappe.local.site)
		wwwdomain = "www."+self.domain_name
		domain_array = self.get_domain_array()
		command=[]
		if domain_config.installed_wildcard_ssl==0 or (domain_config.installed_wildcard_ssl==1 and self.enable_custom_ssl==1):
			# enable www for domain and ssl
			if wwwdomain not in domain_array and domain_config.enable_www==1 and self.disable_www==0:
				commands=["bench setup add-domain {custom_domain} --site {site_name}".format(custom_domain=wwwdomain, site_name=site_name)]
				commands.append("bench setup nginx --yes")		
				commands.append("bench setup reload-nginx")
				frappe.enqueue('go1_cms.utils.utils.run_command', commands=commands, doctype="Site Settings",key=today() + " " + nowtime())
				wwwcommand=["sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=wwwdomain)]
				frappe.enqueue('go1_cms.utils.utils.run_ssl_command',	commands=wwwcommand,doctype="Site Settings",key=today() + " " + nowtime())
			else:
				wwwcommand=["sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=wwwdomain)]
				frappe.enqueue('go1_cms.utils.utils.run_ssl_command',	commands=wwwcommand,doctype="Site Settings",key=today() + " " + nowtime())
	
			# add custom ssl or lets's encrypt ssl	
			command.append("sudo -H bench setup lets-encrypt {site_name} --custom-domain {domain}".format(site_name=site_name, domain=self.domain_name))
			frappe.enqueue('go1_cms.utils.utils.run_ssl_command',	commands=command,doctype="Site Settings",key=today() + " " + nowtime())
			
			
	def connect_external_bench(self):
		'''
		installation
		# env/bin/pip3 install paramiko
		'''
		import paramiko
		domain_config = frappe.get_single('Server Configuration')
		username = getpass.getuser()
		hostname = domain_config.host
		username = domain_config.user_name
		password = domain_config.get_password(fieldname="server_password", raise_exception=False)
		application = domain_config.application_path
		commands = ["cd {application}/&&pwd".format(application=application),"pwd","id","uname -a","df -h"]
		# initialize the SSH client
		client = paramiko.SSHClient()
		# add to known hosts
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			client.connect(hostname=hostname, username=username, password=password)
			print(commands)
			# execute the commands
			for command in commands:
				print("="*50, command, "="*50)
				stdin, stdout, stderr = client.exec_command(command)
				print(stdout.read().decode())
				err = stderr.read().decode()
				print("============123============")
				print(err)
				if err:
					frappe.log_error("Error with connect_external_bench", str(err))
		
		except:
			print("[!] Cannot connect to the SSH Server")
			exit()

	def check_nginx_status(self):
		#service nginx status
		output = self.shell_output('systemctl is-active nginx').replace(" ", "")
		if output!="active":
			frappe.log_error("not active","state")
			self.remove_webconfig()
			

	def shell_output(self, param):
		"""
			This method just takes the shell commands to be executed and returns what
			this command outputs in shell
			:param param: command (example "ls")
			:return: string of commands output on shell
			"""
		try:
			import subprocess
			import sys
			x = ((subprocess.Popen([str(param)],shell=True,#to run in shell
						bufsize=0, 
						stdout=subprocess.PIPE, #to give it to pipe
						stderr=subprocess.PIPE, #to give errors also to pipe
						universal_newlines=False,#shall it include the newline 
					)).communicate()[0]#this is to get the value from shell
				.decode("utf-8")#this is to remove 'b i.e to convert from byte to string
			).strip()
			return x
		except Exception as e:
			frappe.log_error(str(e), "Error with execution in get_str ")
			return e
		
	def on_trash(self):
		
		self.remove_webconfig()

	def remove_webconfig(self):
		domain_config = frappe.get_single('Server Configuration')
		site_name = cstr(frappe.local.site)
		domain_array = self.get_domain_array()
		wwwdomain = "www."+self.domain_name
		if domain_config.setup_domain and self.domain_name in domain_array:
			# remove domain	bench setup sync-domains
			commands = ["bench setup remove-domain {custom_domain} --site {site_name}".format(custom_domain=self.domain_name, site_name=site_name)]
			# remove www subdomain bench setup sync-domains
			if wwwdomain in domain_array:
				commands.append("bench setup remove-domain {custom_domain} --site {site_name}".format(custom_domain=wwwdomain, site_name=site_name))
			frappe.enqueue('go1_cms.utils.utils.run_command', commands=commands, doctype="Site Settings",key=today() + " " + nowtime())
			# setup nginx config and reloading the nginx service		
			#nginxCmd=["bench setup nginx --yes"]
			nginxCmd=["service nginx start"]
			nginxCmd.append("bench setup nginx --yes")
			nginxCmd.append("bench setup reload-nginx")
			frappe.enqueue('go1_cms.utils.utils.run_command', commands=nginxCmd, doctype="Site Settings",key=today() + " " + nowtime())
			
		else:
			commands=["bench setup nginx --yes"]
			commands.append("service nginx start")		
			commands.append("bench setup reload-nginx")
			frappe.enqueue('go1_cms.utils.utils.run_command', commands=commands, doctype="Site Settings",key=today() + " " + nowtime())
			

	def get_domains(self):
		site_name = cstr(frappe.local.site)
		site_config_path = os.path.join(site_name, 'site_config.json')
		with open(site_config_path, 'r') as f:
			site_config_data = json.load(f)
		domains=""
		for i in site_config_data['domains']:
			if type(i) is dict:
				domains += " -d "+i
			else:
				domains += " -d "+i['domain']
		return domains

	def get_wildcard_ssl_enabled_domains(self):
		common_site_config_path = os.path.join('common_site_config.json')
		with open(common_site_config_path, 'r') as f:
			common_site_config_data = json.load(f)
		domains=[]
		#for i in common_site_config_data['wildcard']:
		if common_site_config_data['wildcard']:
			if type(common_site_config_data['wildcard']) is dict:
				domains.append(common_site_config_data['wildcard'])
			else:
				domains.append(common_site_config_data['wildcard']['domain'])
		return domains

	def check_subdomain_with_arecord(self, domain=None, host_ip=None):
		import dns
		import dns.resolver
		'''
		installation
		# env/bin/pip3 install dnspython
		'''
		
		try:
			if not host_ip:
				host_name = socket.gethostname() 
				host_ip = socket.gethostbyname(host_name)
				hostip_ex = socket.gethostbyname_ex(host_name)[2]
			if not domain:
				domain = self.domain_name
			html = "host_name :"+str(host_name)+"\n"
			html += "host_ip :"+str(host_ip)+"\n"
			html += "hostip_ex :"+str(hostip_ex)+"\n"
			html += "domain :"+str(domain)+"\n"
			result = dns.resolver.query(domain, 'A')
			html += "result :"+str(result)+"\n"
			for ipval in result:
				html += "ipval.to_text() :"+str(ipval.to_text())+"\n"
				if ipval.to_text() not in hostip_ex:
					html += "123 :"+str(ipval.to_text())+"\n"
				if hostip_ex.count(ipval.to_text()):
					html += "123==== :"+str(ipval.to_text())+"\n"
				frappe.log_error("check_subdomain_with_arecord", html)
				if not ipval.to_text():
					frappe.throw("{domain} not mapped with A record!".format(domain=domain))
				if ipval.to_text()!=host_ip or ipval.to_text() not in hostip_ex:
					frappe.throw("Domain {domain} not configured with IP.".format(domain=domain))

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.check_subdomain_with_arecord")
			frappe.throw('{0}'.format(e))

	def get_domain_array(self):
		site_name = cstr(frappe.local.site)
		site_config_path = os.path.join(site_name, 'site_config.json')
		with open(site_config_path, 'r') as f:
			site_config_data = json.load(f)
		domains=[]
		for i in site_config_data['domains']:
			if type(i) is dict:
				domains.append(i['domain'])
			else:
				domains.append(i)
		return domains

	def update_domain(self):
		pass

		
@frappe.whitelist()
def process_for_nginx(name):
	try :
		"""
		enque command after code execution
		"""
		site_settings = get_site_settings(name)
		if site_settings:
			process(site_settings[0])
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.process_for_nginx")

def get_site_settings(name):
	"""
	Returns particular `Site Settings` document
	"""
	site_settings = DocType('Site Settings')
	return (
	    frappe.qb.from_(site_settings)
	    .select(site_settings.name)
	    .where(site_settings.name == name)
	).run(as_dict=True)

def process(data):
	"""
	Checks a `Site Settings` and updates it status as necessary
	"""
	if data:
		try:
			web = frappe.get_doc('Site Settings', data['name'])
			web.check_nginx_status()
			frappe.db.commit()
		except frappe.ValidationError:
			frappe.db.rollback()
			frappe.db.begin()
			frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.process(rollback)")
			frappe.db.commit()

@frappe.whitelist()
def execute_bench_command(method, args=None):
	dateTimeObj = datetime.now()
	key = dateTimeObj.strftime("%Y-%m-%d %H:%M:%S.%f")
	if args:
		commands = ["bench execute {method} --args {args}".format(method=method, args=args)]
	else:
		commands = ["{method}".format(method=method)]

	frappe.enqueue('go1_cms.utils.utils.run_command',
		commands=commands,
		doctype="Site Settings",
		key=key
	)

@frappe.whitelist()
def get_domainconfig_settings():
	domain_config = frappe.get_single('Server Configuration')
	return 	domain_config
	
@frappe.whitelist()
def update_domain(name, domain):
	try:
		# check_domains = frappe.db.sql('''select name from `tabSite Settings` where domain_name = %(domain)s or domain = %(domain)s''', {'domain': domain})
		# if check_domains:
		# 	frappe.throw('Domain already in use')
		doc = frappe.get_doc('Site Settings', name)
		domains_list = [doc.domain_name]
		if doc.domain:
			domains_list.append(doc.domain)
		if doc.additional_information:
			update_domain_info(domain, domains_list, doc)
		doc.domain = domain
		doc.enable_alias_active = 0
		if not doc.is_domain_verified:
			doc.is_domain_verified = 1
		doc.save(ignore_permissions=True)
		return {'status': 'success'}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'update_domain')
		return {'status': 'failed'}

def update_domain_info(domain, domains_list, doc):
	add_info = json.loads(doc.additional_information)
	check_url = next((data for data in add_info if data.get('fieldname') == 'web_url'), None)
	if not doc.is_domain_verified:
		check_ip = next((data for data in add_info if data.get('fieldname') == 'domain_ip'), None)
		if check_ip:
			doc.check_subdomain_with_arecord(domain=domain, host_ip=check_ip.get('value'))
	if check_url:
		connection = get_connection(check_url.get('value'))
		if connection:
			site_settings_list = connection.get_list('Site Settings', filters=[['name', 'in', domains_list]], fields=['name', 'domain_name', 'business', 'theme', 'home_page'])
			# opts = None
			# for item in site_settings_list:
			if site_settings_list:
				opts = site_settings_list[0]
				connection.delete('Site Settings', site_settings_list[0].get('name'))
				if not opts: opts = {}
				data = {
					'doctype': 'Site Settings',
					'domain_name': domain,
					'business': opts.get('business') or None,
					'theme': opts.get('theme') or None,
					'home_page': opts.get('home_page') or 'index'
					}
				res = connection.session.post(connection.url + "/api/resource/" + data.get("doctype"),
				data={"data":frappe.as_json(data)}, verify=connection.verify, headers=connection.headers)
				_res, err_msg = None, None
				try:
					_res = res.json()
				except Exception as e:
					pass
				connection.logout()
				if _res:
					if _res.get('_server_messages'):
						msg = json.loads(_res.get('_server_messages'))
						if len(msg) > 0:
							err = json.loads(msg[0])
							if err.get('message'):
								err_msg = err.get('message')
					if err_msg:
						frappe.throw('{0}'.format(err_msg))
			else:
				connection.logout()

@frappe.whitelist()
def make_alias_active(name):
	try:
		doc = frappe.get_doc('Site Settings', name)
		domains_list = []
		if doc.domain:
			domains_list.append(doc.domain)
		if len(domains_list) > 0 and doc.additional_information:
			update_domain_info(doc.domain_name, domains_list, doc)
		doc.enable_alias_active = 1
		doc.save(ignore_permissions=True)
		return {'status': 'success'}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'make_alias_active')

@frappe.whitelist()
def add_custom_domain(name, domain):
	try:
		site_settings = DocType('Site Settings')
		check_domains = (
		    frappe.qb.from_(site_settings)
		    .select(site_settings.name)
		    .where((site_settings.domain_name == domain) | (site_settings.domain == domain))
		).run(as_dict=True)
		if check_domains:
			frappe.throw(frappe._('Domain already in use'))
		doc = frappe.get_doc('Site Settings', name)
		doc.domain = domain
		doc.is_domain_verified = 0
		doc.save(ignore_permissions=True)
		return {'status':'success'}
	except Exception as e:
		return {'status': 'failed'}
