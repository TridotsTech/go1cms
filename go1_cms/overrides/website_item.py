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
        super().get_context(context)
        # website_item = frappe._dict({})
        # website_item.name = context.name
        # website_item.web_item_name = context.web_item_name
        # website_item.route = context.route
        # website_item.has_variants = context.has_variants
        # website_item.variant_of = context.variant_of
        # website_item.item_group = context.item_group
        # website_item.stock_uom = context.stock_uom
        # website_item.brand = context.brand
        # website_item.website_image = context.website_image
        # website_item.short_description = context.short_description
        # website_item.web_long_description = context.web_long_description
        # website_item.recommended_items = context.recommended_items
        # website_item.shopping_cart = context.shopping_cart
        # website_item.slides = [
        #     {'heading': i.heading, 'description': i.description, 'image': i.description} for i in context.slides]

        # context.website_item = website_item
        context.doc_name = self.name
        context.meta_title = self.web_item_name

        if not self.route.endswith('product-123-product-456-product'):
            web_client = frappe.db.get_value(
                'MBW Client Website', {"type_web": "Bản chính"}, pluck='name', as_dict=1)
            if web_client:
                web_item = frappe.db.get_value('MBW Client Website Item', {
                    'parent': web_client, 'parentfield': 'page_websites', 'page_type': 'Product detail page'}, ['page_id'], as_dict=1)

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
