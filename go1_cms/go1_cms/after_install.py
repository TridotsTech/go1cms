# Copyright (c) 2015, Tridotstech Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals, print_function

import frappe
import os
import re
import json
import zipfile
from frappe.utils import encode, get_files_path, getdate, to_timedelta,  flt


def get_all_folder_in_dir(version):
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'mbw_json_data', version)
    return os.listdir(path)


def after_install():
    # * load images
    unzip_section_images()

    # * load setting
    if frappe.db.get_single_value("CMS Settings", "is_updated") == 0:
        insert_cms_settings()

    # * load data doctype
    insert_header_layouts()
    insert_footer_layouts()
    insert_section_groups()
    insert_custom_queries()
    insert_section_templates()
    insert_color_palletes()
    insert_section_component_groups()
    insert_section_components()
    insert_background_masks()
    insert_background_gradients()
    insert_css_fonts()
    insert_menus()
    insert_forms()

    # insert_header_components()
    insert_page_template('header_component_v1')
    # insert_footer_components()
    insert_page_template('footer_component_v1')

    insert_web_theme()
    insert_page_template('page_template_v1')
    insert_website_template()
    insert_faq()
    insert_testimonial()
    insert_blogger()

    # update cms setting
    update_cms_setting()

    # insert_webpage_builder()
    # update_workspace_v14()


def update_cms_setting():
    frappe.db.set_value('CMS Settings', 'CMS Settings', 'is_updated', 1)


# def update_file_setup_template():
#     path = frappe.get_module_path("go1_cms")
#     file_path = os.path.join(
#         path, "setup_template.json")
#     out = {
#         "allow_update": 0
#     }
#     with open(file_path, "w", encoding='utf-8') as f:
#         json.dump(out, f, ensure_ascii=False)


def get_setup_template():
    path = frappe.get_module_path("go1_cms")
    file_path = os.path.join(
        path, "setup_template.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)
        return out
    else:
        return {}


def insert_css_fonts():
    file_name = "css_fonts.json"
    read_module_path(file_name)


def insert_menus():
    # file_name = "menus.json"
    # read_module_path(file_name)

    file_name = "menu.json"
    read_module_path_mbw(file_name)


def insert_forms():
    file_name = "mbw_form.json"
    read_module_path_mbw(file_name)


def insert_header_layouts():
    # file_name = "header_layouts.json"
    # read_module_path(file_name)

    file_name = "header_layout.json"
    read_module_path_mbw(file_name)


def insert_section_components():
    file_name = "section_components.json"
    read_module_path(file_name)


def insert_section_component_groups():
    file_name = "section_component_groups.json"
    read_module_path(file_name)


def insert_footer_layouts():
    # file_name = "footer_layouts.json"
    # read_module_path(file_name)

    file_name = "footer_layout.json"
    read_module_path_mbw(file_name)


def insert_section_groups():
    # file_name = "section_groups.json"
    # read_module_path(file_name)

    file_name = "section_template_group.json"
    read_module_path_mbw(file_name)


def insert_custom_queries():
    file_name = "custom_query.json"
    read_module_path(file_name)


def insert_section_templates():
    # file_name = "section_templates.json"
    # read_module_path(file_name)

    file_name = "section_template.json"
    read_module_path_mbw(file_name)


def insert_color_palletes():
    # file_name = "color_palletes.json"
    # read_module_path(file_name)

    file_name = "color_palette.json"
    read_module_path_mbw(file_name)


def insert_cms_settings():
    # file_name = "cms_settings.json"
    # read_module_path(file_name)

    file_name = "cms_settings.json"
    read_module_path_mbw(file_name)


def insert_background_masks():
    file_name = "background_masks.json"
    read_module_path(file_name)


def insert_background_gradients():
    file_name = "background_gradients.json"
    read_module_path(file_name)


def insert_web_theme():
    # file_name = "web_themes.json"
    # read_module_path(file_name)

    file_name = "web_theme.json"
    read_module_path_mbw(file_name)


def insert_blogger(t=0):
    file_name = "blogger.json"
    read_module_path_mbw(file_name)


def insert_faq():
    file_name = "faq.json"
    read_module_path(file_name)


def insert_testimonial():
    file_name = "testimonial.json"
    read_module_path(file_name)


def insert_page_template(version):
    path = frappe.get_module_path("go1_cms")
    # get setup
    allow_update = get_setup_template().get('allow_update', 0)
    from frappe.model.mapper import get_mapped_doc
    for fd in get_all_folder_in_dir(version):
        file_path = os.path.join(
            path, 'mbw_json_data', version, fd, "page_template.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                out = json.load(f)
            for i in out:
                try:
                    web_section_old = []
                    check_doc = frappe.db.exists(
                        i.get('doctype'), i.get('name'))

                    if not check_doc:
                        # insert if new app or not find doc
                        doc = frappe.get_doc(i).insert()
                    elif str(allow_update) == '1':
                        # update if allow
                        doc = frappe.get_doc(i.get('doctype'), i.get('name'))
                        web_section_old = [i.section for i in doc.web_section]
                        doc.web_section = []

                    # web_sections = i.get("web_section")
                    webpage_section_file_path = os.path.join(
                        path, 'mbw_json_data', version, fd, "section.json")

                    if os.path.exists(webpage_section_file_path):
                        with open(webpage_section_file_path, 'r') as f:
                            header_out = json.load(f)
                        for j in header_out:
                            template = section_name = j.get("section_name")
                            p_doc = get_mapped_doc("Section Template", template, {
                                "Section Template": {
                                    "doctype": "Page Section"
                                },
                                "Section Content": {
                                    "doctype": "Section Content"
                                }
                            }, None, ignore_permissions=True)
                            p_doc.section_title = j.get("section_title")
                            p_doc.section_name = j.get("section_name")
                            if j.get("menu"):
                                p_doc.menu = j.get("menu")
                            if j.get("form"):
                                p_doc.form = j.get("form")
                            if j.get("content"):
                                p_doc.content = []
                                for ct in j.get("content"):
                                    p_doc.append("content", ct)
                            if j.get("web_template"):
                                p_doc.web_template = j.get("web_template")
                            if j.get("css_field_list"):
                                p_doc.css_field_list = j.get(
                                    "css_field_list")
                            if j.get("class_name"):
                                p_doc.class_name = j.get("class_name")
                            if j.get("css_json"):
                                p_doc.css_json = j.get("css_json")
                            if j.get("css_text"):
                                p_doc.css_text = j.get("css_text")
                            p_doc.allow_update_to_style = 0
                            if j.get("allow_update_to_style"):
                                p_doc.allow_update_to_style = j.get(
                                    "allow_update_to_style")
                            p_doc.insert()
                            doc.append("web_section", {
                                "idx": j.get("idx"),
                                "docstatus": 0,
                                "section": p_doc.name,
                                "section_title": j.get("section_title"),
                                "section_type": j.get("section_type"),
                                "content_type": j.get("content_type"),
                                "section_name": j.get("section_name"),
                                "column_index": j.get("column_index"),
                                "allow_update_to_style": p_doc.allow_update_to_style
                            })

                    doc.save()

                    # delete old section if update:
                    if check_doc and str(allow_update) == '1':
                        for sec in web_section_old:
                            frappe.delete_doc('Page Section', sec)

                except frappe.NameError:
                    pass
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(),
                                     "insert_page_template")


def insert_website_template():
    file_name = "mbw_website_template.json"
    read_module_path_mbw(file_name)


def insert_webpage_builder():
    path = frappe.get_module_path("go1_cms")
    from frappe.model.mapper import get_mapped_doc
    file_path = os.path.join(path, 'json_data', "webpage_builder.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)
        for i in out:
            try:
                doc = frappe.get_doc(i).insert()
                web_sections = i.get("web_section")
                webpage_section_file_path = os.path.join(
                    path, 'json_data', "webpage_sections.json")
                if os.path.exists(webpage_section_file_path):
                    with open(webpage_section_file_path, 'r') as f:
                        header_out = json.load(f)
                    for j in header_out:
                        template = section_name = j.get("section_title")
                        p_doc = get_mapped_doc("Section Template", template, {
                            "Section Template": {
                                "doctype": "Page Section"
                            },
                            "Section Content": {
                                "doctype": "Section Content"
                            }
                        }, None, ignore_permissions=True)
                        p_doc.section_title = template
                        p_doc.custom_title = section_name
                        p_doc.choose_from_template = 1
                        p_doc.section_template = template
                        if j.get("content"):
                            p_doc.content = []
                            for ct in j.get("content"):
                                p_doc.append("content", ct)
                        if j.get("web_template"):
                            p_doc.web_template = j.get("web_template")
                        if j.get("css_field_list"):
                            p_doc.css_field_list = j.get("css_field_list")
                        if j.get("class_name"):
                            p_doc.class_name = j.get("class_name")
                        if j.get("css_json"):
                            p_doc.css_json = j.get("css_json")
                        if j.get("css_text"):
                            p_doc.css_text = j.get("css_text")
                        p_doc.allow_update_to_style = 0
                        if j.get("allow_update_to_style"):
                            p_doc.allow_update_to_style = j.get(
                                "allow_update_to_style")
                        p_doc.insert()
                        doc.append("web_section", {
                            "idx": j.get("idx"),
                            "docstatus": 0,
                            "section": p_doc.name,
                            "section_title": template,
                            "section_type": j.get("section_type"),
                            "allow_update_to_style": p_doc.allow_update_to_style
                        })

                doc.save()
            except frappe.NameError:
                pass
            except Exception as e:
                frappe.log_error(frappe.get_traceback(),
                                 "insert_webpage_builder")


def insert_header_components():
    path = frappe.get_module_path("go1_cms")
    from frappe.model.mapper import get_mapped_doc
    # file_path = os.path.join(path, 'json_data', "header_components.json")
    # header_sec_file_path = os.path.join(
    #     path, 'json_data', "header_sections.json")

    file_path = os.path.join(
        path, 'mbw_json_data', "header_component.json")
    header_sec_file_path = os.path.join(
        path, 'mbw_json_data', "header_sections.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)
        for i in out:
            try:
                doc = frappe.get_doc(i).insert()
                web_sections = i.get("web_section")
                if os.path.exists(header_sec_file_path):
                    with open(header_sec_file_path, 'r') as f:
                        header_out = json.load(f)
                    for j in header_out:
                        template = section_name = j.get("section_title")
                        p_doc = get_mapped_doc("Section Template", template, {
                            "Section Template": {
                                "doctype": "Page Section"
                            },
                            "Section Content": {
                                "doctype": "Section Content"
                            }
                        }, None, ignore_permissions=True)
                        p_doc.section_title = template
                        p_doc.custom_title = section_name
                        p_doc.choose_from_template = 1
                        p_doc.section_template = template
                        if j.get("section_type") == "Menu":
                            p_doc.menu = j.get("menu")
                        p_doc.save(ignore_permissions=True)
                        doc.append("web_section", {
                            "idx": j.get("idx"),
                            "docstatus": 0,
                            "section": p_doc.name,
                            "section_title": template,
                            "section_type": j.get("section_type"),
                            "allow_update_to_style": 0,
                            "column_index": j.get("column_index"),
                        })
                doc.save()
            except frappe.NameError:
                pass
            except Exception as e:
                frappe.log_error(frappe.get_traceback(),
                                 "Header Component Insertion")


def insert_footer_components():
    path = frappe.get_module_path("go1_cms")
    from frappe.model.mapper import get_mapped_doc
    # file_path = os.path.join(path, 'json_data', "footer_components.json")
    # footer_sec_file_path = os.path.join(
    #     path, 'json_data', "footer_sections.json")

    file_path = os.path.join(
        path, 'mbw_json_data', "footer_component.json")
    footer_sec_file_path = os.path.join(
        path, 'mbw_json_data', "footer_sections.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)
        for i in out:
            try:
                doc = frappe.get_doc(i).insert()
                web_sections = i.get("web_section")
                if os.path.exists(footer_sec_file_path):
                    with open(footer_sec_file_path, 'r') as f:
                        header_out = json.load(f)
                    for j in header_out:
                        template = section_name = j.get("section_title")
                        p_doc = get_mapped_doc("Section Template", template, {
                            "Section Template": {
                                "doctype": "Page Section"
                            },
                            "Section Content": {
                                "doctype": "Section Content"
                            }
                        }, None, ignore_permissions=True)
                        p_doc.section_title = template
                        p_doc.custom_title = section_name
                        p_doc.choose_from_template = 1
                        p_doc.section_template = template
                        if j.get("section_type") == "Menu":
                            p_doc.menu = j.get("menu")
                            p_doc.content[0].content = j.get("menu")
                        p_doc.save(ignore_permissions=True)
                        doc.append("web_section", {
                            "idx": j.get("idx"),
                            "docstatus": 0,
                            "section": p_doc.name,
                            "section_title": template,
                            "section_type": j.get("section_type"),
                            "allow_update_to_style": 0,
                            "column_index": j.get("column_index"),
                        })
                doc.save()
            except frappe.NameError:
                pass
            except Exception as e:
                frappe.log_error(frappe.get_traceback(),
                                 "Footer Component Insertion")


def read_module_path(file_name):
    path = frappe.get_module_path("go1_cms")
    file_path = os.path.join(path, 'json_data', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)
        for i in out:
            try:
                frappe.get_doc(i).insert()
            except frappe.NameError:
                pass
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), file_name)


def read_module_path_mbw(file_name):
    allow_update = get_setup_template().get('allow_update', 0)

    path = frappe.get_module_path("go1_cms")
    file_path = os.path.join(path, 'mbw_json_data', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)
        for i in out:
            try:
                check_doc = frappe.db.exists(
                    i.get('doctype'), i.get('name'))

                if not check_doc:
                    # insert if new app or not find doc
                    frappe.get_doc(i).insert()
                elif str(allow_update) == '1':
                    # update if allow
                    doc = frappe.get_doc(
                        i.get('doctype'), i.get('name')).as_dict()
                    data_update = {}
                    for x, y in i.items():
                        if x not in ['name']:
                            if frappe.get_meta(i.get('doctype')).has_field(x):
                                if type(y) not in [list]:
                                    data_update[x] = y
                                else:
                                    # delete old data table
                                    for child in doc[x]:
                                        frappe.delete_doc(
                                            child.get('doctype'), child.get('name'))
                                    for child in y:
                                        frappe.get_doc(child).insert()

                    frappe.db.set_value(
                        i.get('doctype'), i.get('name'), data_update)

                    # call save
                    doc = frappe.get_doc(i.get('doctype'), i.get('name'))
                    doc.save()

            except frappe.NameError:
                pass
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), file_name)


def unzip_section_images():
    """Unzip current file and replace it by its children"""
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
            origin = get_files_path()
            item_file_path = os.path.join(origin, file.filename.split("/")[1])
            if not os.path.exists(item_file_path):
                file_doc = frappe.new_doc("File")
                file_doc.content = z.read(file.filename)
                file_doc.file_name = filename
                file_doc.folder = "Home"
                file_doc.is_private = 0
                file_doc.save()


@frappe.whitelist()
def load_sample_pages():
    frappe.enqueue(insert_sample_pages, queue='default')


def insert_sample_pages():
    pages_list = [{"json_file": "about_us.json", "sections_file": "about_us_sections.json"}, {"json_file": "our_team.json", "sections_file": "our_team_sections.json"}, {"json_file": "testimonials.json", "sections_file": "testimonials_sections.json"}
                  ]
    path = frappe.get_module_path("go1_cms")
    from frappe.model.mapper import get_mapped_doc
    for page in pages_list:
        file_path = os.path.join(
            path, 'json_data', "sample_pages", page.get("json_file"))
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                out = json.load(f)
            for i in out:
                try:
                    if not frappe.db.get_all("Web Page Builder", filters={"page_title": i.get("page_title")}):
                        doc = frappe.get_doc(i).insert()
                        web_sections = i.get("web_section")
                        webpage_section_file_path = os.path.join(
                            path, 'json_data', "sample_pages", page.get("sections_file"))
                        if os.path.exists(webpage_section_file_path):
                            with open(webpage_section_file_path, 'r') as f:
                                header_out = json.load(f)
                            for j in header_out:
                                template = section_name = j.get(
                                    "section_title")
                                p_doc = get_mapped_doc("Section Template", template, {
                                    "Section Template": {
                                        "doctype": "Page Section"
                                    },
                                    "Section Content": {
                                        "doctype": "Section Content"
                                    }
                                }, None, ignore_permissions=True)
                                p_doc.section_title = template
                                p_doc.custom_title = section_name
                                p_doc.choose_from_template = 1
                                p_doc.section_template = template
                                if j.get("content"):
                                    p_doc.content = []
                                    for ct in j.get("content"):
                                        p_doc.append("content", ct)
                                if j.get("web_template"):
                                    p_doc.web_template = j.get("web_template")
                                if j.get("css_field_list"):
                                    p_doc.css_field_list = j.get(
                                        "css_field_list")
                                if j.get("class_name"):
                                    p_doc.class_name = j.get("class_name")
                                if j.get("css_json"):
                                    p_doc.css_json = j.get("css_json")
                                if j.get("css_text"):
                                    p_doc.css_text = j.get("css_text")
                                p_doc.allow_update_to_style = 0
                                if j.get("allow_update_to_style"):
                                    p_doc.allow_update_to_style = j.get(
                                        "allow_update_to_style")
                                p_doc.insert()
                                doc.append("web_section", {
                                    "idx": j.get("idx"),
                                    "docstatus": 0,
                                    "section": p_doc.name,
                                    "section_title": template,
                                    "section_type": j.get("section_type"),
                                    "allow_update_to_style": p_doc.allow_update_to_style
                                })

                        doc.save()
                except frappe.NameError:
                    pass
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(),
                                     "insert_sample_page")
    frappe.publish_realtime('msgprint', 'Sample pages are created.')


def update_workspace_v14():
    try:
        from frappe.utils.change_log import get_versions
        installed_apps_details = get_versions()
        if installed_apps_details:
            if 'frappe' in list(installed_apps_details.keys()):
                frappe_version = installed_apps_details.get(
                    'frappe').get('version')
                if int(frappe_version.split('.')[0]) >= 14:
                    path = frappe.get_module_path("go1_cms")
                    file_path = os.path.join(
                        path, 'json_data', "workspacev14.json")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            out = json.load(f)
                            for i in out:
                                try:
                                    frappe.get_doc(i).insert()
                                except frappe.NameError:
                                    pass
                                except Exception as e:
                                    frappe.log_error(
                                        frappe.get_traceback(), "workspacev14.json")

                elif int(frappe_version.split('.')[0]) <= 13:
                    path = frappe.get_module_path("go1_cms")
                    file_path = os.path.join(
                        path, 'json_data', "workspacev13.json")
                    if os.path.exists(file_path):
                        with open(file_path, 'r') as f:
                            out = json.load(f)
                            for i in out:
                                try:
                                    frappe.get_doc(i).insert()
                                except frappe.NameError:
                                    pass
                                except Exception as e:
                                    frappe.log_error(
                                        frappe.get_traceback(), "workspacev13.json")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "update_workspace_v14")
