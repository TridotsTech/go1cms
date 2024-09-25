from mimetypes import guess_type
import frappe
from frappe import _, local
from pypika import functions as fn
from go1_cms.api.common import (
    pretty_date,
    convert_str_to_list
)
from go1_cms.api.website.log_page import (
    log_page_view
)
from datetime import datetime
import math
from io import BytesIO
from captcha.image import ImageCaptcha
import string
import random
import base64
from frappe.utils import cint
from frappe.utils import now, add_to_date


@frappe.whitelist(allow_guest=True)
def get_filter_job():
    job_type = frappe.db.get_all('Employment Type', fields=[
                                 'employee_type_name as label', 'employee_type_name as value'], order_by='creation')
    job_location = frappe.db.get_all(
        'Branch', fields=['branch as label', 'branch as value'], order_by='creation asc')
    job_department = frappe.db.get_all(
        'Department', fields=['department_name as label', 'name as value'], order_by='creation asc')

    job_designation = frappe.db.get_all('Designation', fields=[
        'designation_name as label', 'designation_name as value'], order_by='creation')
    # job_designation.insert(0, {
    #     "label": "Tất cả",
    #     "value": "",
    # })
    return {
        'job_type': job_type,
        'job_location': job_location,
        'job_department': job_department,
        'job_designation': job_designation,
        'range_salary': {
            'from': 0,
            'to': 0
        }
    }


@frappe.whitelist(allow_guest=True)
def get_all_job(name_section, **kwargs):
    try:
        page_no = int(kwargs.get('page_no', 1)) - 1
        page_no = 0 if page_no < 1 else page_no
    except:
        page_no = 0

    page_len = 8
    text_search = kwargs.get('text_search', '')

    job_location = convert_str_to_list(kwargs.get('job_location', []))
    job_department = convert_str_to_list(kwargs.get('job_department', []))
    job_designation = convert_str_to_list(kwargs.get('job_designation', []))
    range_salary = convert_str_to_list(
        kwargs.get('range_salary', [None, None]))
    job_type = convert_str_to_list(kwargs.get('job_type', []))

    sort_by = frappe.qb.desc
    if kwargs.get('sort_by', 'desc').lower() == "asc":
        sort_by = frappe.qb.asc

    JobOpening = frappe.qb.DocType('Job Opening')

    doc_section = frappe.get_doc('Page Section', name_section)
    sort_field = doc_section.sort_field if doc_section.sort_field else 'posted_on'
    limit = doc_section.no_of_records if doc_section.no_of_records else page_len
    offset = page_no*limit

    # get data
    m_query = (frappe.qb.from_(JobOpening))
    if text_search:
        m_query = m_query.where(
            JobOpening.job_title.like('%' + text_search+'%'))
    if job_location:
        m_query = m_query.where(JobOpening.location.isin(job_location))
    if job_type:
        m_query = m_query.where(JobOpening.employment_type.isin(job_type))
    if job_department:
        m_query = m_query.where(JobOpening.department.isin(job_department))
    if job_designation:
        m_query = m_query.where(JobOpening.designation.isin(job_designation))

    if isinstance(range_salary, list):
        q = None
        salary_from = range_salary[0]
        salary_to = range_salary[1]

        if salary_from != None:
            salary_from = int(salary_from)
        if salary_to != None:
            salary_to = int(salary_to)

        if salary_from != None and salary_to == None:
            q = (JobOpening.upper_range >= salary_from)
        elif salary_from == None and salary_to != None:
            q = (JobOpening.lower_range <= salary_to)
        elif salary_from != None and salary_to != None:
            q = ((JobOpening.lower_range <= salary_to) & (
                JobOpening.upper_range >= salary_from))
        if q:
            m_query = m_query.where(q)
    q_data = m_query.select(JobOpening.name, JobOpening.job_title, JobOpening.posted_on,
                            JobOpening.location, JobOpening.employment_type, JobOpening.lower_range,
                            JobOpening.upper_range, JobOpening.publish_salary_range, JobOpening.salary_per, JobOpening.department, JobOpening.route, JobOpening.vacancies, JobOpening.job_requisition, JobOpening.designation, JobOpening.currency
                            ).offset(offset).limit(limit).orderby(JobOpening[sort_field], order=sort_by)

    jobs = q_data.run(as_dict=True)

    for j in jobs:
        j['pretty_posted_on'] = pretty_date(j.posted_on)

    q_count = m_query.select(fn.Count('*').as_('total'))
    rs_count = q_count.run(as_dict=True)
    if rs_count and limit > 0:
        total_page = math.ceil(rs_count[0].total/limit)
    else:
        total_page = 0
    pagination = {
        'current_page': page_no + 1,
        'total': rs_count[0].total if rs_count and limit > 0 else 0,
        'total_page': total_page,
        'limit': limit,
    }
    return {'data': jobs, 'pagination': pagination}


@frappe.whitelist(allow_guest=True)
def get_job_detail(name):
    if frappe.db.exists("Job Opening", name):
        doc = frappe.db.get_value('Job Opening', name, [
                                  'name', 'company', 'job_title', 'designation', 'status', 'posted_on', 'closes_on', 'closed_on', 'employment_type', 'department', 'location', 'publish_applications_received', 'description', 'currency', 'lower_range', 'upper_range', 'salary_per', 'publish_salary_range', 'route', 'job_requisition', 'vacancies'], as_dict=1)
        return doc
    else:
        frappe.throw(_('Không tìm thấy công việc ứng tuyển'),
                     frappe.DoesNotExistError)


@frappe.whitelist(allow_guest=True)
def get_job_related(name, **kwargs):
    jobs = []
    if frappe.db.exists("Job Opening", name):
        doc = frappe.db.get_value('Job Opening', name, [
            'name', 'job_title', 'designation', 'status', 'employment_type', 'location'], as_dict=1)

        name_section = kwargs.get('name_section', None)
        if name_section:
            doc_section = frappe.db.get_value('Page Section', name_section, [
                                              'no_of_records'], as_dict=1)
            limit = doc_section.no_of_records if doc_section.no_of_records else 4
        else:
            limit = kwargs.get('limit', '4')
            if limit.isdigit():
                limit = int(limit) if int(limit) <= 12 else 12
            else:
                limit = 4

        JobOpening = frappe.qb.DocType('Job Opening')
        m_query = (frappe.qb.from_(JobOpening).where(
            (JobOpening.name != name)))
        q = None

        if doc.location:
            q = (q | (JobOpening.location == doc.location)) if q else (
                JobOpening.location == doc.location)
        if doc.designation:
            q = (q | (JobOpening.designation == doc.designation)) if q else (
                JobOpening.designation == doc.designation)
        if doc.employment_type:
            q = (q | (JobOpening.employment_type == doc.employment_type)) if q else (
                JobOpening.employment_type == doc.employment_type)
        if doc.job_title:
            q = (q | (JobOpening.job_title.like('%' + doc.job_title+'%'))) if q else (
                JobOpening.job_title.like('%' + doc.job_title+'%'))

        if q:
            m_query = m_query.where(q)
        q_data = m_query.select(JobOpening.name, JobOpening.job_title, JobOpening.posted_on,
                                JobOpening.location, JobOpening.employment_type, JobOpening.lower_range,
                                JobOpening.upper_range, JobOpening.publish_salary_range, JobOpening.salary_per, JobOpening.department, JobOpening.vacancies, JobOpening.job_requisition, JobOpening.designation, JobOpening.currency
                                ).limit(limit).orderby(JobOpening.posted_on, order=frappe.qb.desc)

        jobs = q_data.run(as_dict=True)
        for j in jobs:
            j['pretty_posted_on'] = pretty_date(j.posted_on)

    return {"jobs": jobs}


@frappe.whitelist(methods=['POST'], allow_guest=True)
def upload_cv(name_job, **kwargs):
    applicant_name = kwargs.get('full_name', None)
    email = kwargs.get('email', None)
    phone_number = kwargs.get('phone_number', None)
    message = kwargs.get('message', None)
    files = frappe.request.files
    captcha_text = kwargs.get('captcha_text', None)
    form_name = kwargs.get('form_name', None)
    job_opening = kwargs.get('job_opening', None)
    ip = local.request.remote_addr

    if not form_name or not frappe.db.exists("MBW Form", form_name):
        frappe.throw('Mã biểu mẫu không đúng')

    captcha = frappe.db.get_value('CMS Captcha', {
        "ip": ip, 'captcha_text': captcha_text}, ['name', 'creation'], as_dict=1)
    if not captcha_text or not captcha:
        return {
            'status': '0',
            'msg': 'Mã captcha không đúng'
        }

    old_datetime = datetime.strptime(
        add_to_date(now(), minutes=-10), "%Y-%m-%d %H:%M:%S.%f")
    if old_datetime >= captcha.creation:
        return {
            'status': '1',
            'msg': 'Mã captcha đã hết hạn'
        }

    if not applicant_name:
        frappe.throw('Họ tên không được để trống')
    if not email:
        frappe.throw('Email không được để trống')
    if not phone_number:
        frappe.throw('Số điện thoại không được để trống')

    if frappe.db.exists("Job Opening", name_job):
        new_doc = frappe.new_doc('Job Applicant')
        new_doc.applicant_name = applicant_name
        new_doc.email_id = email
        new_doc.phone_number = phone_number
        new_doc.cover_letter = message
        new_doc.job_title = job_opening
        new_doc.save(ignore_permissions=True)
        new_doc.reload()

        filename = ''
        if 'file_cv' in files:
            file_cv = files["file_cv"]
            content = file_cv.stream.read()
            filename = file_cv.filename
            ct = datetime.now()

            file_cv.seek(0, 2)
            size = file_cv.tell()
            file_cv.seek(0)

            str_ts = str(math.floor(ct.timestamp()))
            sp_fn = filename.split('.')
            if len(sp_fn) == 2:
                filename = sp_fn[0] + '_' + str_ts + '.' + sp_fn[1]

            content_type = guess_type(filename)[0]
            if content_type != "application/pdf":
                frappe.throw('Tên tệp không đúng định dạng')

            form_fields = frappe.db.get_all("MBW Form Item", filters={"parent": form_name, "parentfield": "form_fields", "field_name": "file_cv"}, fields=[
                'max_file_size'
            ])
            if not form_fields or form_fields[0].max_file_size*1024**2 < size:
                frappe.throw(
                    f'Tệp không vượt quá {form_fields[0].max_file_size}MB')

            new_file = frappe.get_doc(
                {
                    "doctype": "File",
                    "attached_to_doctype": "Job Applicant",
                    "attached_to_name": new_doc.name,
                    "attached_to_field": "resume_attachment",
                    "folder": "Home",
                    "file_name": filename,
                    "file_url": "",
                    "is_private": 0,
                    "content": content,
                }
            )
            new_file.save(ignore_permissions=True)
            new_doc.resume_attachment = new_file.file_url

        new_doc.save(ignore_permissions=True)

        frappe.enqueue(log_page_view, queue='default', ip=ip,
                       form_type="Form tuyển dụng")
        # delete captcha
        frappe.db.delete("CMS Captcha", {'name': captcha.name})

        return {'status': '200', 'name': new_doc.name}
    else:
        frappe.throw(_('Không tìm thấy công việc ứng tuyển'),
                     frappe.DoesNotExistError)
