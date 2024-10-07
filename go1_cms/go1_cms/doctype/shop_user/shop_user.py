# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from go1_cms.utils.setup import get_settings_from_domain
from frappe.utils.password import update_password as _update_password

class ShopUser(Document):
	def validate(self):		
		if self.get('__islocal'):
			sgs=frappe.db.sql('''select u.* from `tabUser` u,`tabHas Role` r where r.parent=u.name and r.role="Vendor" and email=%(email)s''',{'email':self.email},as_dict=1)
			if sgs:
				frappe.throw("E-Mail ID already registered")
		if not self.full_name:
			self.full_name=self.first_name+' '+(self.last_name if self.last_name else '')
		else:
			if not (self.full_name==self.first_name+' '+(self.last_name if self.last_name else '')):
				self.full_name=self.first_name+' '+(self.last_name if self.last_name else '')
		if self.restaurant and not self.role:
			self.role='Vendor'
		# if self.mobile_no:
		# 	self.validate_phone()
		# if self.set_new_password:
		# 	self.validate_pwd()
		
	def on_update(self):		
		if self.set_new_password:
			self.new_password=self.set_new_password
			frappe.db.set_value('Shop User',self.name,'new_password',self.set_new_password)
		if self.email:
			s = frappe.db.get_all("User", fields=["full_name","email","mobile_no"] , filters={"email": self.email},limit_page_length=1)
			if s:				
				update_user(self)
				if self.new_password:
					update_password(new_password=self.new_password,user=self.name)
					frappe.db.set_value('Shop User',self.name,'set_new_password','')
			else:					
				d = frappe.db.sql("""select name from `tabUser` where email = %(email)s """,{'email':self.email})
				if d: 							
					frappe.throw("E-Mail ID Already Registered")
				else:					
					user=insert_user(self)
					if user:
						if self.new_password:
							newupdate=update_password(new_password=self.new_password, old_password=None,user=self.email)								
							frappe.db.set_value('Shop User',self.name,'set_new_password','')							
		if self.role:
			add_arole(self)
		check_user_permission(self)
		# self.insert_as_customer()

	def insert_as_customer(self):
		customer=frappe.db.get_all('Customers',filters={'user_id':self.name})
		if not customer:
			customer=frappe.get_doc({
				"doctype":"Customers",
				"first_name":self.first_name,
				"last_name":self.last_name,
				"phone":self.mobile_no,
				"email":self.email,
				"user_id":self.email,
				"new_password":self.set_new_password
				}).insert(ignore_permissions=True)
	
	def on_trash(self):
		if self.restaurant and self.email:
			perm=frappe.db.get_all('User Permission',fields=['*'],filters={'user':self.email,'for_value':self.restaurant,'allow':'Business'})
			if perm:
				perm_doc=frappe.get_doc('User Permission',perm[0].name)
				perm_doc.delete()

	# def validate_phone(self):
	# 	order_settings = get_settings_from_domain('Order Settings')
	# 	import re
	# 	res = re.search('(?=.*\d)[\d]', str(self.mobile_no))
	# 	if not res:
	# 		frappe.throw(frappe._('Mobile number must contain only numbers'))
	# 	if order_settings.enable_phone_validation:
	# 		if len(str(self.mobile_no)) != int(order_settings.max_phone_length):
	# 			frappe.throw(frappe._('Phone Number must contain {0} digits').format(order_settings.max_phone_length))

	# def validate_pwd(self):
	# 	order_settings = get_settings_from_domain('Order Settings')
	# 	if len(self.set_new_password) < int(order_settings.min_password_length):
	# 		frappe.throw(frappe._('Password must contain {0} digits').format(order_settings.min_password_length))
	# 	from go1_cms.go1_cms.doctype.order_settings.order_settings import validate_password
	# 	validate_password(self.set_new_password)

def update_user(self):	
	try:
		frappe.db.set_value("User", self.email , "first_name", self.first_name)
		frappe.db.set_value("User", self.email , "mobile_no", self.mobile_no)
		frappe.db.set_value("User", self.email ,"last_name", self.last_name)
		# add_arole(self)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.shop_user.update_user") 	

@frappe.whitelist()
def add_arole(self):	
	if self.restaurant or self.role == 'Shipping Manager':
		user_role=frappe.db.get_all('Has Role',filters={'parent':self.email,'role':self.role})
		if not user_role:
			doc = frappe.get_doc('User',self.name)
			doc.append('roles',{
				'role': self.role
			})
			doc.save(ignore_permissions=True)
			# result= frappe.get_doc({
			# 	"doctype": "Has Role",
			# 	"name": nowdate(),
			# 	"parent": self.email,
			# 	"parentfield": "roles",
			# 	"parenttype": "User",
			# 	"role": self.role
			# 	}).insert(ignore_permissions=True)	
			
@frappe.whitelist(allow_guest=True)
def insert_user(self):	
	from frappe.utils import random_string
	key = random_string(32)
	result= frappe.get_doc({
		"doctype": "User","email": self.email,"first_name": self.first_name,"last_name": self.last_name,
		"mobile_no":self.mobile_no,"send_welcome_email":0,"reset_password_key":key
	}).insert(ignore_permissions=True)
	# add_arole(self)
	return result
	
@frappe.whitelist(allow_guest=True)
def update_password(new_password, logout_all_sessions=0, key=None, old_password=None,user=None):
	try:
		if not user: user=frappe.session.user
		if not key:
			from frappe.utils import random_string
			key = random_string(32)		
			frappe.db.set_value('User', user, 'reset_password_key', key)
		res = _get_user_for_update_password(key, old_password)
		if res.get('message'):
			return res['message']
		else:
			user = res['user']

		_update_password(user, new_password, logout_all_sessions=int(logout_all_sessions))

		user_doc, redirect_url = reset_user_data(user)

		# get redirect url from cache
		redirect_to = frappe.cache().hget('redirect_after_login', user)
		if redirect_to:
			redirect_url = redirect_to
			frappe.cache().hdel('redirect_after_login', user)

		# frappe.local.login_manager.login_as(user)

		if user_doc.user_type == "System User":
			return "/desk"
		else:
			return redirect_url if redirect_url else "/"
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store.ecommerce_business_store.doctype.customers.update_password") 
	
def _get_user_for_update_password(key, old_password):
	try:
		# verify old password
		if key:
			user = frappe.db.get_value("User", {"reset_password_key": key})
			if not user:
				return {
					'message': _("Cannot Update: Incorrect / Expired Link.")
				}

		elif old_password:
			# verify old password
			frappe.local.login_manager.check_password(frappe.session.user, old_password)
			user = frappe.session.user

		else:
			return

		return {
			'user': user
		}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store.ecommerce_business_store.doctype.customers._get_user_for_update_password") 

def reset_user_data(user):
	try:
		user_doc = frappe.get_doc("User", user)
		redirect_url = user_doc.redirect_url
		user_doc.reset_password_key = ''
		user_doc.redirect_url = ''
		user_doc.save(ignore_permissions=True)
		return user_doc, redirect_url
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store.ecommerce_business_store.doctype.customers.reset_user_data") 

	
@frappe.whitelist()
def check_user_permission(self):
	try:
		if self.restaurant and self.email:
			perm=frappe.db.get_all('User Permission',fields=['*'],filters={'user':self.email,'for_value':self.restaurant,'allow':'Business'})
			if not perm:
				frappe.db.sql('''delete from `tabUser Permission` where user=%(user)s and allow="Business"''',{'user':self.email})
				from frappe.utils import random_string
				key = random_string(10)
				frappe.db.sql('''insert into `tabUser Permission` (name,user,allow,for_value) values (%(name)s,%(email)s,"Business",%(restaurant)s)''',{'name':key,'email':self.email,'restaurant':self.restaurant})
	except Exception:
		frappe.log_error(frappe.get_traceback(), "go1_cms.go1_cms.doctype.shop_user.check_user_permission") 
	