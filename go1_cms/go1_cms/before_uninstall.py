from __future__ import unicode_literals, print_function

import frappe
import os
import re
import json
import zipfile
from frappe.utils import encode, get_files_path, getdate, to_timedelta,  flt


def before_uninstall():
    delete_section_images()


def delete_section_images():
    path = frappe.get_module_path("go1_cms")
    file_path = os.path.join(path, "section_images.zip")
    with zipfile.ZipFile(file_path) as z:
        for file in z.filelist:
            if file.is_dir() or file.filename.startswith("__MACOSX/"):
                # skip directories and macos hidden directory
                continue
            filename = os.path.basename(file.filename)
            if filename.startswith("."):
                # skip hidden files
                continue
            arr_filename = file.filename.split("/")
            if len(arr_filename) == 3:
                item_file_path = os.path.join('/files', arr_filename[2])

                # * delete file
                filters = [
                    ['file_url', '=', item_file_path],
                    ['attached_to_doctype', 'is', 'set'],
                    ['attached_to_name', 'is', 'set'],
                    ['attached_to_doctype', 'is', 'set']
                ]
                files = frappe.get_all('File', filters=filters, pluck="name")
                for f in files:
                    frappe.delete_doc('File', f)
