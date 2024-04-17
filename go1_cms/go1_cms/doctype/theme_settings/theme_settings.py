# Copyright (c) 2022, Tridotstech and contributors
# For license information, please see license.txt

import frappe
import json
import os
from frappe.utils import get_files_path
from frappe.model.document import Document


class ThemeSettings(Document):
    def on_update(self):
        try:
            path, sitename = get_path_name()
            if path:
                template = frappe.get_template("templates/includes/themes.css")
                folder_name = self.name.lower().replace(' ', '-')
                if not os.path.exists(os.path.join(path, 'public', "webthemes")):
                    frappe.create_folder(os.path.join(
                        path, 'public', "webthemes"))
                if not os.path.exists(os.path.join(path, 'public', "webthemes", folder_name)):
                    frappe.create_folder(os.path.join(
                        path, 'public', "webthemes", folder_name))
                with open(os.path.join(path, 'public', "webthemes", folder_name, ('theme.css')), "w") as f:
                    doc_obj = self
                    doc_obj.page_css = (self.page_css.replace('\n', ''))
                    theme_css = template.render({'doc': doc_obj})
                    # from go1_cms.utils.setup import minify_string
                    frappe.log_error(theme_css, "theme_css")
                    f.write(minify_string(theme_css))
                fpath = "/assets/{0}/webthemes/{1}/theme.css".format(
                    sitename, folder_name)
                if self.file_path != fpath:
                    frappe.db.set_value(
                        'Theme Settings', self.name, 'file_path', fpath)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "theme")


@frappe.whitelist()
def minify_string(html):
    import re
    # return_String =  htmlmin.minify(html.replace('\n',''),pre_tags=(u'pre', u'textarea', u'style',u'script'),remove_comments=True,remove_all_empty_space=True,remove_optional_attribute_quotes=False)
    return_String = html.replace('\n', '')
    return re.sub(">\s*<", "><", return_String)


@frappe.whitelist()
def get_path_name():
    path = sitename = None
    if "go1_cms" in frappe.get_installed_apps():
        path = frappe.get_app_path("go1_cms")
        sitename = 'go1_cms'
    return path, sitename


# try:
# 	frappe.log_error(self.page_css,"calling")
# 	path = get_files_path()
# 	if not os.path.exists(os.path.join(path,'theme.css')):
# 		css_content = ''
# 		if self.google_fonts:
# 			for d in self.google_fonts:
# 				css_content += d.font_family_url
# 		if self.page_css:
# 			css_content += self.page_css
# 		frappe.log_error(css_content,"css_content1")
# 		if css_content:
# 			frappe.log_error(css_content,"css_content")
# 			with open(os.path.join(path,('theme.css')), "w") as f:
# 				f.write(css_content)
# except Exception as e:
# frappe.log_error(frappe.get_traceback(),"generate_css_file")
