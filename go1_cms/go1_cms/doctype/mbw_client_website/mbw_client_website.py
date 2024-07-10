# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWClientWebsite(Document):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Tên Website",
                "type": "Data",
                "key": "name_web",
                "width": "276px"
            },
            {
                "label": "Loại mẫu",
                "type": "Select",
                "key": "type_template",
                "width": "228px"
            },
            {
                "label": "Loại website",
                "type": "Select",
                "key": "type_web",
                "width": "116px"
            },
            {
                "label": "Kích hoạt",
                "type": "Check",
                "key": "published",
                "width": "149px"
            },
            {
                "label": "Chỉnh sửa",
                "type": "Check",
                "key": "edit",
                "width": "149px"
            },
            {
                "label": "Hành động",
                "key": "action_button"
            }
        ]

        rows = [
            "name",
            "creation",
            "modified_by",
            "_assign",
            "owner",
            "action_button",
            "name_web",
            "type_template",
            "modified",
            "type_web",
            "edit",
            "published",
            "route_web"
        ]
        return {'columns': columns, 'rows': rows}

    def validate(self):
        try:
            if frappe.db.exists('MBW Client Website', self.name):
                doc_self_old = frappe.get_doc('MBW Client Website', self.name)
            else:
                doc_self_old = frappe._dict({})
            # check status web
            if doc_self_old.type_web != self.type_web and self.type_web == 'Bản chính':
                existing_list = frappe.db.get_all(
                    "MBW Client Website",
                    filters={"name": ("!=", self.name),
                             "type_web": "Bản chính"},
                    fields=['name'],
                )
                if existing_list:
                    doc = frappe.get_doc(
                        'MBW Client Website', existing_list[0].get('name'))
                    doc.type_web = "Bản nháp"
                    doc.save()

            # check edit
            # if self.edit == 1:
            #     existing_list = frappe.db.sql(
            #         '''UPDATE `tabMBW Client Website` SET edit=0 WHERE name!="{web_name}" AND edit=1'''.format(web_name=self.name))
            #     frappe.db.commit()

            # update published
            if doc_self_old.published != self.published:
                for item in self.page_websites:
                    if item.page_type not in ['News detail page', 'New page']:
                        doc = frappe.get_doc('Web Page Builder', item.page_id)
                        doc.published = self.published
                        doc.save()

            if doc_self_old.type_web != self.type_web or not doc_self_old.route_web:
                """ check published, set route page, update menu """
                router_menu_draft = "/template_" + frappe.scrub(
                    self.name)
                for item in self.page_websites:
                    route_template = ""
                    doc = frappe.get_doc('Web Page Builder', item.page_id)

                    if self.type_web == 'Bản chính':
                        if item.route_template and item.route_template[0] == '/':
                            route_template = item.route_template[1:]
                        else:
                            route_template = item.route_template
                    else:
                        route_template = 'template_' + frappe.scrub(
                            self.name) + item.route_template
                    doc.route_template = route_template
                    doc.route_prefix = '' if self.type_web == 'Bản chính' else router_menu_draft
                    doc.save()

                # update redirect url menu
                menus = frappe.db.get_all(
                    "Menu",
                    filters={"id_client_website": self.name, 'is_template': 0},
                    fields=['name']
                )

                for mn in menus:
                    menu_items = frappe.db.get_all(
                        "Menus Item",
                        filters={"parent": mn.name,
                                 "parentfield": "menus"},
                        fields=['name', 'redirect_url']
                    )

                    for m in menu_items:
                        redirect_url = m.redirect_url or '#'
                        if not redirect_url.startswith('http'):
                            if self.type_web == 'Bản chính' and redirect_url.startswith(router_menu_draft):
                                redirect_url = redirect_url.replace(
                                    router_menu_draft, "", 1)
                            elif self.type_web == 'Bản nháp' and not redirect_url.startswith(router_menu_draft):
                                redirect_url = router_menu_draft + redirect_url

                            frappe.db.set_value('Menus Item', m.name, {
                                'redirect_url': redirect_url
                            })

            # set route website
            route_web = ''
            if self.type_web == 'Bản chính' and self.page_websites:
                route_web = self.page_websites[0].route_template
            elif self.page_websites:
                route_web = '/template_' + frappe.scrub(
                    self.name) + self.page_websites[0].route_template
            self.route_web = route_web or ''
        except Exception as e:
            frappe.log_error(frappe.get_traceback(),
                             "validate MBW Client Website")

    def after_delete(self):
        list_header = []
        list_footer = []
        for item in self.page_websites:
            doc = frappe.get_doc('Web Page Builder', item.page_id)
            if doc.header_component and doc.header_component not in list_header:
                list_header.append(doc.header_component)
            if doc.footer_component and doc.footer_component not in list_footer:
                list_footer.append(doc.footer_component)

            frappe.delete_doc('Web Page Builder', item.page_id)

        # delete web theme
        if self.web_theme:
            frappe.delete_doc('Web Theme', self.web_theme)

        # delete header and footer
        for x in list_header:
            frappe.delete_doc('Header Component', x)
        for x in list_footer:
            frappe.delete_doc('Footer Component', x)

        # delete menu
        menus = frappe.db.get_all(
            "Menu",
            filters={"id_client_website": self.name, 'is_template': 0},
            fields=['name']
        )
        for n in menus:
            frappe.delete_doc('Menu', n.name)

        # delete MBW Form
        mbw_forms = frappe.db.get_all(
            "MBW Form",
            filters={"id_client_website": self.name, 'is_template': 0},
            fields=['name']
        )
        for f in mbw_forms:
            frappe.delete_doc('MBW Form', f.name)
