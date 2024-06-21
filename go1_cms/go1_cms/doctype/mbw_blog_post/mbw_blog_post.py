# Copyright (c) 2024, Tridotstech and contributors
# For license information, please see license.txt
from math import ceil

import frappe
from frappe import _
from frappe.utils import (
    cint,
    get_fullname,
    global_date_format,
    markdown,
    sanitize_html,
    strip_html_tags,
    today,
)
from frappe.website.utils import (
    clear_cache,
    find_first_image,
    get_comment_list,
    get_html_content_based_on_type,
)
from slugify import slugify

from frappe.website.website_generator import WebsiteGenerator


class MbwBlogPost(WebsiteGenerator):
    @staticmethod
    def default_list_data():
        columns = [
            {
                "label": "Tiêu đề",
                "type": "Data",
                "key": "title",
                "width": "10rem"
            },
            {
                "label": "Danh mục",
                "type": "Link",
                "key": "blog_category",
                "width": "10rem"
            },
            {
                "label": "Ngày đăng",
                "type": "Date",
                "key": "published_on",
                "width": "315px"
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
            "_assign", "owner",
            "title",
            "modified",
            "blog_category",
            "published_on",
            "action_button"
        ]
        return {'columns': columns, 'rows': rows}

    # @frappe.whitelist()
    # def make_route(self):
    #     if not self.route:
    #         return (
    #             slugify(frappe.db.get_value(
    #                 "Blog Category", self.blog_category, "title"))
    #             + "/"
    #             + slugify(self.title)
    #         )

    def validate(self):
        if not self.route:
            self.route = "tin-tuc/" + slugify(self.title) + f"-{self.name}"

        if not self.blog_intro:
            content = get_html_content_based_on_type(
                self, "content", self.content_type)
            self.blog_intro = content[:200]
            self.blog_intro = strip_html_tags(self.blog_intro)

        if self.blog_intro:
            self.blog_intro = self.blog_intro[:200]

        if not self.meta_title:
            self.meta_title = self.title[:60]
        else:
            self.meta_title = self.meta_title[:60]

        if not self.meta_description:
            self.meta_description = self.blog_intro[:140]
        else:
            self.meta_description = self.meta_description[:140]

        if self.published and not self.published_on:
            self.published_on = today()

        if self.featured:
            if not self.meta_image:
                frappe.throw(_("A featured post must have a cover image"))
            self.reset_featured_for_other_blogs()

        self.set_read_time()

    def set_read_time(self):
        content = self.content or self.content_html or ""
        if self.content_type == "Markdown":
            content = markdown(self.content_md)

        total_words = len(strip_html_tags(content).split())
        self.read_time = ceil(total_words / 250)

    def get_context(self, context):
        context.blog_name = self.name

        web_client = frappe.db.get_value(
            'MBW Client Website', {"type_web": "Bản chính"}, as_dict=1)
        if web_client:
            page_blog = frappe.db.get_value('MBW Client Website Item', {
                                            'parent': web_client.name, 'parentfield': 'page_websites', 'page_type': 'News detail page'}, ['page_id'], as_dict=1)
            if page_blog:
                if frappe.db.exists('Web Page Builder', page_blog.page_id, cache=True):
                    doc_wpb = frappe.get_doc(
                        'Web Page Builder', page_blog.page_id)
                    doc_wpb.get_context(context)
