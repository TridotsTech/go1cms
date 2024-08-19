import frappe
from hrms.hr.doctype.job_opening.job_opening import JobOpening


class CustomJobOpening(JobOpening):
    website = frappe._dict(
        template="go1_cms/templates/generators/job_opening.html",
        condition_field="publish",
        page_title_field="job_title",
    )

    def validate(self):
        if not self.route or not self.route.startswith('cong-viec/'):
            self.route = f"cong-viec/{frappe.scrub(self.job_title).replace('_', '-')}"

        super().validate()

    def get_context(self, context):
        context.doc_name = self.name
        if not self.route.endswith('jobs-123-jobs-456-jobs'):
            web_client = frappe.db.get_value(
                'MBW Client Website', {"type_web": "Bản chính"}, pluck='name', as_dict=1)
            if web_client:
                web_item = frappe.db.get_value('MBW Client Website Item', {
                    'parent': web_client, 'parentfield': 'page_websites', 'page_type': 'Job detail page'}, ['page_id'], as_dict=1)

                if web_item and frappe.db.exists('Web Page Builder', web_item.page_id, cache=True):
                    doc_wpb = frappe.get_doc(
                        'Web Page Builder', web_item.page_id)
                    doc_wpb.get_context(context)
        else:
            web_test = frappe.db.exists('Web Page Builder', {
                'route': 'jobs-123-jobs-456-jobs'}, cache=True)
            if web_test:
                doc_wpb = frappe.get_doc(
                    'Web Page Builder', web_test)
                doc_wpb.get_context(context)

        super().get_context(context)
