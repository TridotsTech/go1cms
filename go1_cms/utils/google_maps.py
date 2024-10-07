#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe, json
import requests

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

@frappe.whitelist(allow_guest=True)
def get_geolocation(address):
	try:
		maps = frappe.get_single('Google Settings')
		if maps.enable:
			params = {'key': maps.api_key, 'address': address}
			req = requests.get(GEOCODE_URL, params=params)
			res = req.json()
			if res['status'] == 'OK':
				result = res['results'][0]
				latitude = result['geometry']['location']['lat']
				longitude = result['geometry']['location']['lng']
				return {
					'address': address,
					'latitude': latitude,
					'longitude': longitude,
					'address_components': res['results'][0]['address_components']
					}
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.utils.google_maps.get_geolocation')

def reverse_geocode(latitude, longitude):
	try:
		maps = frappe.get_single('Google Settings')
		if maps.enable:
			params = {
				'key': maps.api_key,
				'latlng': '{0},{1}'.format(latitude, longitude)
			}
			req = requests.get(GEOCODE_URL, params=params)
			res = req.json()
			if res['status'] == 'OK':
				result = res['results'][0]
				return result
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'go1_cms.utils.google_maps.reverse_geocode')
