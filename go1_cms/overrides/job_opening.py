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
            'MBW Client Website', {"type_web": "Bản chính"}, pluck='name', as_dict=1)
        if web_client:
            page_id = frappe.db.get_value('MBW Client Website Item', {
                'parent': web_client, 'parentfield': 'page_websites', 'page_type': 'Job detail page'}, pluck='page_id', as_dict=1)

            web_test = frappe.db.exists('Web Page Builder', {
                'route': 'jobs/software-developer'}, cache=True)
            if page_id and frappe.db.exists('Web Page Builder', page_id, cache=True):
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', page_id)
                doc_wpb.get_context(context)
            elif web_test:
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', web_test)
                doc_wpb.get_context(context)

        super().get_context(context)
