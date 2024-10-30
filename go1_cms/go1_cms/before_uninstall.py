from __future__ import unicode_literals, print_function

import frappe
import os
import re
import json
import zipfile
from frappe.utils import encode, get_files_path, getdate, to_timedelta,  flt


def before_uninstall():
    frappe.db.set_value('CMS Settings', 'CMS Settings', 'is_updated', 0)
    delete_section_images()


def delete_section_images():
    import tarfile
    path = frappe.get_module_path("go1_cms")
    file_path = os.path.join(path, "section_images.tar")
    with tarfile.open(file_path, 'r') as tar:
        for member in tar.getmembers():
            if member.isdir():
                continue
            filename = os.path.basename(member.name)
            if filename.startswith("."):
                # skip hidden files
                continue

            arr_filename = member.name.split("/")
            if len(arr_filename) == 3:
                with tar.extractfile(member) as file:
                    if file is not None:
                        item_file_path = os.path.join(
                            '/files', arr_filename[2])
                        # * delete file
                        filters = [
                            ['file_url', '=', item_file_path],
                        ]
                        files = frappe.get_all(
                            'File', filters=filters, pluck="name")
                        for f in files:
                            frappe.delete_doc('File', f)
