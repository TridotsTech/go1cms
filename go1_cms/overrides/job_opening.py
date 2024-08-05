import frappe
from hrms.hr.doctype.job_opening.job_opening import JobOpening


class CustomJobOpening(JobOpening):
    website = frappe._dict(
        template="go1_cms/templates/generators/job_opening.html",
        condition_field="publish",
        page_title_field="job_title",
    )

    def get_context(self, context):
        context.doc_name = self.name

        web_client = frappe.db.get_value(
            'MBW Client Website', {"type_web": "Bản chính"}, as_dict=1)
        if web_client:
            page_blog = frappe.db.get_value('MBW Client Website Item', {
                'parent': web_client.name, 'parentfield': 'page_websites', 'page_type': 'Job detail page'}, ['page_id'], as_dict=1)

            if page_blog and frappe.db.exists('Web Page Builder', page_blog.page_id, cache=True):
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', page_blog.page_id)
                doc_wpb.get_context(context)
            elif frappe.db.exists('Web Page Builder', 'test-job-detail', cache=True):
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', 'test-job-detail')
                doc_wpb.get_context(context)

        super().get_context(context)
