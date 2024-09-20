import frappe
from webshop.webshop.doctype.website_item.website_item import WebsiteItem
from frappe.utils import random_string


class CustomWebsiteItem(WebsiteItem):
    website = frappe._dict(
        template="go1_cms/templates/generators/website_item.html",
        condition_field="published",
        page_title_field="web_item_name",
    )

    def validate(self):
        if not self.route or not self.route.startswith('san-pham/'):
            self.route = f"san-pham/{frappe.scrub(self.web_item_name).replace('_', '-')}-{random_string(6)}"

        super().validate()

    def get_info(self):
        context = frappe._dict({'route': ''})
        super().get_context(context)
        return context

    def get_context(self, context):
        # super().get_context(context)
        context.doc_name = self.name
        context.meta_title = self.web_item_name

        if not self.route.endswith('product-123-product-456-product'):
            web_client = frappe.db.get_value(
                'MBW Client Website', {"type_web": "Bản chính"}, pluck='name', as_dict=1)
            if web_client:
                web_item = frappe.db.get_value('MBW Client Website Item', {
                    'parent': web_client, 'parentfield': 'page_websites', 'page_type': 'Trang chi tiết sản phẩm'}, ['page_id'], as_dict=1)

                if web_item and frappe.db.exists('Web Page Builder', web_item.page_id, cache=True):
                    doc_wpb = frappe.get_doc(
                        'Web Page Builder', web_item.page_id)
                    doc_wpb.get_context(context)
        else:
            web_test = frappe.db.exists('Web Page Builder', {
                'route': 'product-123-product-456-product'}, cache=True)
            if web_test:
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', web_test)
                doc_wpb.get_context(context)
