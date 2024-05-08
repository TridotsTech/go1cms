# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MBWClientWebsite(Document):
    def validate(self):
        try:
            doc_self_old = frappe.get_doc('MBW Client Website', self.name)
            # check status web
            if doc_self_old.status_web != self.status_web and self.status_web == 'Bản chính':
                existing_list = frappe.db.get_all(
                    "MBW Client Website",
                    filters={"name": ("!=", self.name),
                             "status_web": "Bản chính"},
                    fields=['name'],
                )
                if existing_list:
                    doc = frappe.get_doc(
                        'MBW Client Website', existing_list[0].get('name'))
                    doc.status_web = "Bản nháp"
                    doc.save()

            # check edit
            # if self.edit == 1:
            #     existing_list = frappe.db.sql(
            #         '''UPDATE `tabMBW Client Website` SET edit=0 WHERE name!="{web_name}" AND edit=1'''.format(web_name=self.name))
            #     frappe.db.commit()

            if doc_self_old.status_web != self.status_web or doc_self_old.route_web == None:
                list_cpn = []
                """ check published, set route page, update menu """
                router_menu_draft = "/template_" + frappe.scrub(
                    self.name)

                for item in self.page_websites:
                    route_template = ""
                    doc = frappe.get_doc('Web Page Builder', item.page_id)
                    if doc.header_component and doc.header_component not in list_cpn:
                        list_cpn.append(doc.header_component)
                    if doc.footer_component and doc.footer_component not in list_cpn:
                        list_cpn.append(doc.footer_component)

                    doc.published = self.published
                    if self.status_web == 'Bản chính':
                        if item.route_template and item.route_template[0] == '/':
                            route_template = item.route_template[1:]
                        else:
                            route_template = item.route_template
                    else:
                        route_template = 'template_' + frappe.scrub(
                            self.name) + item.route_template
                    doc.route_template = route_template
                    doc.route_prefix = '' if self.status_web == 'Bản chính' else router_menu_draft
                    doc.save()

                # update menu header and footer
                for x in list_cpn:
                    web_sections = frappe.db.get_all(
                        "Mobile Page Section",
                        filters={"parent": x, "parentfield": "web_section"},
                        fields=['section']
                    )
                    for w in web_sections:
                        doc_page = frappe.get_doc('Page Section', w.section)
                        if doc_page.section_type == "Menu":
                            menu_items = frappe.db.get_all(
                                "Menus Item",
                                filters={"parent": doc_page.menu,
                                         "parentfield": "menus"},
                                fields=['name', 'redirect_url']
                            )

                            for m in menu_items:
                                redirect_url = m.redirect_url or '#'
                                if not redirect_url.startswith('http'):
                                    if self.status_web == 'Bản chính' and redirect_url.startswith(router_menu_draft):
                                        redirect_url = redirect_url.replace(
                                            router_menu_draft, "", 1)
                                    elif self.status_web == 'Bản nháp' and not redirect_url.startswith(router_menu_draft):
                                        redirect_url = router_menu_draft + redirect_url

                                    frappe.db.set_value('Menus Item', m.name, {
                                        'redirect_url': redirect_url
                                    })

            # set route website
            route_web = ''
            if self.status_web == 'Bản chính' and self.page_websites:
                route_web = self.page_websites[0].route_template
            else:
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

        # delete header and footer
        for x in list_header:
            web_sections = frappe.db.get_all(
                "Mobile Page Section",
                filters={"parent": x, "parentfield": "web_section"},
                fields=['section']
            )

            list_menu = []
            for w in web_sections:
                doc = frappe.get_doc('Page Section', w.section)
                if doc.section_type == "Menu":
                    list_menu.append(doc.menu)
            frappe.delete_doc('Header Component', x)
            for n in list_menu:
                frappe.delete_doc('Menu', n)

        for x in list_footer:
            web_sections = frappe.db.get_all(
                "Mobile Page Section",
                filters={"parent": x, "parentfield": "web_section"},
                fields=['section']
            )

            list_menu = []
            for w in web_sections:
                doc = frappe.get_doc('Page Section', w.section)
                if doc.section_type == "Menu":
                    list_menu.append(doc.menu)
            frappe.delete_doc('Footer Component', x)
            for n in list_menu:
                frappe.delete_doc('Menu', n)
