import frappe
from frappe.desk.form.load import get_attachments
from slugify import slugify
import zipfile
import shutil
from frappe.utils import get_files_path
import json
import os
import requests
from go1_cms.api.common import (
    convert_data_to_str,
    remove_nulls,
    write_page_section,
    save_images_to_folder,
    create_zip_archive_of_the_folder,
    remove_file_duplicate,
    delete_file_or_folder,
    get_files_attach
)


@frappe.whitelist(allow_guest=True)
def install_template(name):
    if not frappe.db.exists("MBW Website Template", name):
        return False

    template_name = slugify(text=name, separator='_')
    file_name = template_name + '.tar'
    path = os.path.join(frappe.get_module_path(
        "go1_cms"), 'files_zip', 'files_install')
    zip_file_path = os.path.join(path, file_name)
    destination_folder = os.path.join(path, template_name)
    files_path_remove = [zip_file_path, destination_folder]

    try:
        # check folder not exists then create folder
        os.makedirs(path, exist_ok=True)
        # delete old file or folder
        delete_file_or_folder(files_path_remove)

        # download file
        url = frappe.db.get_value(
            'MBW Website Template', name, 'link_download')
        if not url:
            return False
        response = requests.get(url)
        if response.status_code == 200:
            with open(zip_file_path, 'wb') as file:
                file.write(response.content)
        else:
            return False

        # check exists file
        if not os.path.exists(zip_file_path):
            return False
        # unzip file .tar
        shutil.unpack_archive(zip_file_path, destination_folder)

        # install file image, css
        path_images = os.path.join(destination_folder, 'section_images')
        unzip_section_images(path_images, 'css')
        unzip_section_images(path_images, 'section_images')

        # install header component
        insert_page_template(destination_folder, 'header_component')
        # install footer component
        insert_page_template(destination_folder, 'footer_component')
        # install page template
        insert_page_template(destination_folder, 'page_template')
        # install theme
        read_module_path_mbw(destination_folder, 'web_theme.json')
        # install web template
        read_module_path_mbw(destination_folder,
                             'mbw_website_template.json', 1)
        # install section template
        read_module_path_mbw(destination_folder,
                             'section_template.json')

        delete_file_or_folder(files_path_remove)
        return True
    except Exception as ex:
        print('ex::', ex)
        delete_file_or_folder(files_path_remove)
        return False


@frappe.whitelist(allow_guest=True)
def export_template():
    doctype = 'MBW Website Template'
    temp_names = frappe.db.get_all(doctype, pluck='name')
    for docname in temp_names:
        # delete old file
        template_name = slugify(text=docname, separator='_')
        path = os.path.join(frappe.get_module_path("go1_cms"),
                            'files_zip', 'files_download', template_name)
        delete_file_or_folder([path])

        files_attach = []
        web_template = frappe.get_doc(doctype, docname)
        # write file doctype reference web template
        handle_write_multiple_files_web_template(web_template)

        # get file in web template
        remove_file_duplicate(
            files_attach, get_files_attach(doctype, docname))

        # get file in web theme
        if web_template.web_theme:
            remove_file_duplicate(
                files_attach, get_files_attach('Web Theme', web_template.web_theme))

        # get file in Header Component
        if web_template.header_component:
            files = get_files_attach(
                'Header Component', web_template.header_component)
            remove_file_duplicate(files_attach, files)

            # get file in pages
            files = [f for f in get_files_pages(
                web_template.header_component, 'Header Component')]
            remove_file_duplicate(files_attach, files)
            # create file
            write_file_header_component(web_template.header_component, docname)

        # get file in Footer Component
        if web_template.footer_component:
            files = get_files_attach(
                'Footer Component', web_template.footer_component)
            remove_file_duplicate(files_attach, files)

            # get file in pages
            files = [f for f in get_files_pages(
                web_template.footer_component, 'Footer Component')]
            remove_file_duplicate(files_attach, files)
            # create file
            write_file_footer_component(web_template.footer_component, docname)

        # get file in page templates
        print("==================START: write file page template==================")
        for page in web_template.page_templates:
            print(page.page_template)
            files = get_files_attach('Page Template', page.page_template)
            remove_file_duplicate(files_attach, files)

            # get file in pages
            files = [f for f in get_files_pages(
                page.page_template, 'Page Template')]
            remove_file_duplicate(files_attach, files)

            # create file
            write_file_page_template(page.page_template, docname)
        print("==================END: write file page template==================")

        ### save images to folder ###
        print("==================START: save images to folder=================")
        path = os.path.join(frappe.get_module_path("go1_cms"),
                            'files_zip', 'files_download', template_name, 'section_images')
        # file image
        print("===>>: image")
        save_images_to_folder(files_attach, path, 'section_images')

        # file css
        print("===>>: css")
        files_css = ['aos.css', 'cms.css', 'desk.min.css',
                     'owl.carousel.min.css', 'site_custom_css.css']
        save_images_to_folder(files_css, path, 'css')
        print("==================END: save images to folder=================")

        # create file zip
        print("==================START: create file zip==================")
        path = os.path.join(frappe.get_module_path("go1_cms"),
                            'files_zip', 'files_download')
        files_path_remove = []
        create_zip_archive_of_the_folder(path, docname, docname)
        print("==================END: create file zip==================")

    return {'msg': "Done"}


def get_files_pages(parent, parenttype, parentfield="web_section"):
    files_attach = []
    web_section = frappe.db.get_all(
        "Mobile Page Section", filters={
            "parent": parent, "parentfield": parentfield, 'parenttype': parenttype}, fields=['section'], order_by="idx"
    )
    for sec in web_section:
        files = [f for f in get_files_page(sec.section)]
        remove_file_duplicate(files_attach, files)

    return files_attach


def get_files_page(section):
    files = get_files_attach('Page Section', section)

    # get file in field list
    field_list = frappe.db.get_all(
        "Section Content", filters={
            "parent": section, "parentfield": "content"}, fields=['field_type', 'content', 'fields_json'], order_by="idx"
    )
    for field in field_list:
        if field.field_type == "List":
            fields_attach = []
            try:
                fields_json = json.loads(field.fields_json)
                for f in fields_json:
                    if f.get('field_type') == 'Attach':
                        fields_attach.append(f.get('field_key'))
                content = json.loads(field.content)
                for item in content:
                    for f in fields_attach:
                        if item[f] and item[f].startswith('/files/'):
                            file_name = item[f].split('/files/')[1]
                            if file_name and file_name not in files:
                                files.append(file_name)
            except Exception as ex:
                print('=========Error========', ex)
        elif field.field_type == 'Attach':
            try:
                if field.content and field.content.startswith('/files/'):
                    file_name = field.content.split('/files/')[1]
                    if file_name and file_name not in files:
                        files.append(file_name)
            except Exception as ex:
                print('=========Error========', ex)

    return files


def handle_write_multiple_files_web_template(web_template):
    print('==================START: handle_write_multiple_files_web_template==================')
    doctypes = [
        'Section Template', 'Web Theme', 'MBW Website Template'
    ]
    web_sections = []
    # section in header
    if web_template.header_component:
        header_cp = frappe.get_doc(
            'Header Component', web_template.header_component)
        for sec in header_cp.web_section:
            web_sections.append(sec.section)
    # section in footer
    if web_template.footer_component:
        footer_cp = frappe.get_doc(
            'Footer Component', web_template.footer_component)
        for sec in footer_cp.web_section:
            web_sections.append(sec.section)

    # section in page template
    for page in web_template.page_templates:
        page_temp = frappe.get_doc('Page Template', page.page_template)
        for sec in page_temp.web_section:
            web_sections.append(sec.section)
    section_template = frappe.db.get_all(
        "Page Section", filters=[['name', 'in', web_sections]], pluck='section_name')
    section_template = list(set(section_template))

    for doctype in doctypes:
        filters = []
        if doctype == "Web Theme":
            filters = [['name', '=', web_template.web_theme]]
        elif doctype == "Section Template":
            filters = [['name', 'in', section_template]]
        elif doctype == "MBW Website Template":
            filters = [['name', '=', web_template.name]]
        write_file_doctype(web_template.name, doctype, filters)
    print('==================END: handle_write_multiple_files_web_template==================')


def write_file_header_component(name, template_name, version='header_component'):
    print("==================START: write file header==================")
    folder_name = slugify(text=name, separator='_')
    template_name = slugify(text=template_name, separator='_')
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'files_zip', 'files_download', template_name, version, folder_name)

    header_comp = frappe.get_doc('Header Component', name).as_dict()
    header_comp['web_section'] = []
    # remove fields is None
    header_comp = remove_nulls(header_comp)

    # check folder not exists then create folder
    os.makedirs(path, exist_ok=True)

    # write file page
    json_file_name = "page_template.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump([header_comp], f, ensure_ascii=False,
                  default=convert_data_to_str)

    # write file sections
    write_page_section(name, path, 'Header Component')
    print("==================END: write file header==================")


def write_file_footer_component(name, template_name, version='footer_component'):
    print("==================START: write file footer==================")
    folder_name = slugify(text=name, separator='_')
    template_name = slugify(text=template_name, separator='_')
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'files_zip', 'files_download', template_name, version, folder_name)

    footer_comp = frappe.get_doc('Footer Component', name).as_dict()
    footer_comp['web_section'] = []
    # remove fields is None
    footer_comp = remove_nulls(footer_comp)

    # check folder not exists then create folder
    os.makedirs(path, exist_ok=True)

    # write file
    json_file_name = "page_template.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump([footer_comp], f, ensure_ascii=False,
                  default=convert_data_to_str)

    # sections
    write_page_section(name, path, 'Footer Component')
    print("==================END: write file footer==================")


def write_file_doctype(template_name, doctype, filters=[]):
    print('==================START: write_file_doctype==================')
    template_name = slugify(text=template_name, separator='_')
    doc_names = frappe.db.get_all(doctype, filters, pluck="name")

    files_attach = []
    data = []
    print('===>>Doctype:', doctype)
    for docname in doc_names:
        print(docname)
        # get file attach
        files = get_files_attach(doctype, docname)
        remove_file_duplicate(files_attach, files)

        d_j = frappe.get_doc(doctype, docname).as_dict()
        # remove fields is None
        d_j = remove_nulls(d_j)

        # reset web template
        if doctype == 'MBW Website Template':
            d_j['template_in_use'] = 0
            d_j['installed_template'] = 0

        data.append(d_j)

    # write file
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'files_zip', 'files_download', template_name)

    # check folder not exists then create folder
    os.makedirs(path, exist_ok=True)

    folder_name = slugify(text=doctype, separator='_')
    json_file_name = "{0}.json".format(folder_name)
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, default=convert_data_to_str)

    # save file image
    print("==================START: save images to folder=================")
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'files_zip', 'files_download', template_name, 'section_images')
    save_images_to_folder(files_attach, path, 'section_images')
    print("==================END: save images to folder=================")

    print('==================END: write_file_doctype==================')


def write_file_page_template(name, template_name, version='page_template'):
    folder_name = slugify(text=name, separator='_')
    template_name = slugify(text=template_name, separator='_')
    path = os.path.join(frappe.get_module_path("go1_cms"),
                        'files_zip', 'files_download', template_name, version, folder_name)

    page_temp = frappe.get_doc('Page Template', name).as_dict()
    page_temp['web_section'] = []
    page_temp['mobile_section'] = []
    # remove fields is None
    page_temp = remove_nulls(page_temp)

    # check folder not exists then create folder
    os.makedirs(path, exist_ok=True)

    # write file
    json_file_name = "page_template.json"
    with open(os.path.join(path, json_file_name), "w", encoding='utf-8') as f:
        json.dump([page_temp], f, ensure_ascii=False,
                  default=convert_data_to_str)

    # sections
    write_page_section(name, path, "Page Template")


def get_all_folder_in_dir(path, version):
    path = os.path.join(path, version)
    return os.listdir(path)


def insert_page_template(path, version, allow_update=0):
    # get setup
    from frappe.model.mapper import get_mapped_doc
    for fd in get_all_folder_in_dir(path, version):
        file_path = os.path.join(
            path, version, fd, "page_template.json")
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
                        doc.reload()
                    else:
                        # update if allow
                        doc = frappe.get_doc(i.get('doctype'), i.get('name'))
                        web_section_old = [i.section for i in doc.web_section]
                        doc.web_section = []

                    if not check_doc or allow_update == 1:
                        # insert section
                        section_file_path = os.path.join(
                            path, version, fd, "section.json")

                        if os.path.exists(section_file_path):
                            with open(section_file_path, 'r') as f:
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
                        # save
                        doc.save()

                        # delete old section if update:
                        for sec in web_section_old:
                            frappe.delete_doc('Page Section', sec)

                except frappe.NameError:
                    pass
                except Exception as e:
                    frappe.log_error(frappe.get_traceback(),
                                     "insert_page_template")


def read_module_path_mbw(path, file_name, allow_update=0):
    file_path = os.path.join(path, file_name)

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            out = json.load(f)

        for i in out:
            try:
                if not frappe.db.exists(i.get('doctype'), i.get('name')):
                    # insert if new app or not find doc
                    doc = frappe.get_doc(i)
                    doc.flags.ignore_permissions = True
                    doc.flags.ignore_mandatory = True
                    doc.insert()
                elif allow_update == 1:
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


def unzip_section_images(path, folder_name):
    """Unzip current file and replace it by its children"""
    origin = get_files_path()
    file_path = os.path.join(path, folder_name)
    for fd in get_all_folder_in_dir(path, folder_name):
        try:
            image_file_path = os.path.join(file_path, fd)
            item_file_path = os.path.join(origin, fd)
            if fd.lower().endswith('.svg') or fd.lower().endswith('.css'):
                with open(image_file_path, 'r') as file:
                    content = file.read()
            else:
                with open(image_file_path, 'rb') as file:
                    content = file.read()

            if not os.path.exists(item_file_path):
                file_doc = frappe.new_doc("File")
                file_doc.content = content
                file_doc.file_name = fd
                file_doc.folder = "Home"
                file_doc.is_private = 0
                file_doc.save()

        except Exception as ex:
            print('ex:: unzip_section_images===>>', ex)
