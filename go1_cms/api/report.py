import frappe
from frappe import _
from datetime import datetime, timedelta


def calc_trang_xem_nhieu_nhat(time_start, time_end):
    qr_trang_xem_nhieu = f"""
        SELECT Count(session_id) AS `luot_xem`,
            site_title AS `trang`
        FROM `tabCMS Access`
        WHERE time_access >= '{time_start}'
        AND time_access <= '{time_end}'
        AND site_title IS NOT NULL
        GROUP BY site_title
        ORDER BY luot_xem DESC
        LIMIT 5
        """
    rs = frappe.db.sql(qr_trang_xem_nhieu, as_dict=1)
    rows = []
    data = []
    for item in rs:
        rows.append(item.trang)
        data.append({
            "name": item.trang,
            "value": item.luot_xem
        })

    return {
        "rows": rows,
        "data": data,
    }


def calc_trang_xem_nhieu_nhat_ky_truoc(time_start, time_end, titles=[]):
    data = {}
    titles = [i for i in titles if i]
    str_title = "', '".join(titles)
    qr_trang_xem_nhieu = f"""
        SELECT Count(session_id) AS `luot_xem`,
            site_title AS `trang`
        FROM `tabCMS Access`
        WHERE time_access >= '{time_start}'
        AND time_access <= '{time_end}'
        AND site_title IS NOT NULL
        AND site_title IN ('{str_title}')
        GROUP BY site_title
        ORDER BY luot_xem DESC
        LIMIT 5
        """
    rs = frappe.db.sql(qr_trang_xem_nhieu, as_dict=1)
    for item in rs:
        data[item.trang] = item.luot_xem

    return data


def calc_summary_report(time_start, time_end):
    te = (datetime.strptime(
        time_end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    # so_nguoi_dung
    qr_so_nguoi_dung = f"""
        SELECT COUNT(DISTINCT ip) AS so_nguoi_dung
        FROM `tabCMS Session`
        WHERE time_access >= '{time_start}'
        AND time_access <= '{te}'
        """
    so_nguoi_dung = frappe.db.sql(qr_so_nguoi_dung, as_dict=1)[
        0]['so_nguoi_dung']

    # so_phien_truy_cap
    qr_so_truy_cap = f"""
        SELECT COUNT(*) AS phien_truy_cap
        FROM `tabCMS Session`
        WHERE time_access >= '{time_start}'
        AND time_access <= '{te}'
        """
    so_truy_cap = frappe.db.sql(qr_so_truy_cap, as_dict=1)[
        0]['phien_truy_cap']

    # thoi gian trung binh
    qr_tg_tb = f"""
        SELECT AVG(tb1.tg_truy_cap) AS average_access_duration
        FROM (
                SELECT ip,
                    TIMESTAMPDIFF(SECOND, time_access, time_out) AS tg_truy_cap
                FROM `tabCMS Session`
                WHERE time_access >= '{time_start}'
                AND time_access <= '{te}'
            ) AS tb1
        """
    tg_tb = frappe.db.sql(qr_tg_tb, as_dict=1)[
        0]['average_access_duration']

    # luot truy cap truoc
    qr_luot_truy_cap = f"""
        WITH RECURSIVE DateRange AS (
                SELECT '{time_end}' AS `date`
            UNION ALL SELECT DATE_SUB(`date`, INTERVAL 1 DAY)
                FROM DateRange
                WHERE DATE_SUB(`date`, INTERVAL 1 DAY) >= '{time_start}'
            ) SELECT d.date AS `name`,
            COALESCE(COUNT(a.ip), 0) AS `value`
        FROM DateRange d
        LEFT JOIN `tabCMS Session` AS a
            ON DATE(a.time_access) = d.date
        GROUP BY d.date
        ORDER BY d.date;
        """
    luot_truy_cap = frappe.db.sql(qr_luot_truy_cap, as_dict=1)
    rows_luot_truy_cap = []
    for i in luot_truy_cap:
        i['name'] = datetime.strptime(
            i.name, '%Y-%m-%d').strftime('%d/%m/%Y')
        rows_luot_truy_cap.append(i.name)

    # so luot dien form
    qr_luot_dien_form = f"""
        WITH RECURSIVE DateRange AS (
                SELECT '{time_end}' AS `date`
            UNION ALL 
            SELECT DATE_SUB(`date`, INTERVAL 1 DAY)
            FROM DateRange
            WHERE DATE_SUB(`date`, INTERVAL 1 DAY) >= '{time_start}'
        )
        SELECT d.date AS `name`,
            COALESCE(COUNT(a.time_request), 0) AS `value`
        FROM DateRange d
        LEFT JOIN `tabCMS Totals Signed Form` AS a
            ON DATE(a.time_request) = d.date
        GROUP BY d.date
        ORDER BY d.date;
        """
    luot_dien_form = frappe.db.sql(qr_luot_dien_form, as_dict=1)
    rows_luot_dien_form = []
    for i in luot_dien_form:
        i['name'] = datetime.strptime(
            i.name, '%Y-%m-%d').strftime('%d/%m/%Y')
        rows_luot_dien_form.append(i.name)

    return {
        "luot_truy_cap": {
            "columns": rows_luot_truy_cap,
            "data": luot_truy_cap
        },
        "thoi_gian_xem_tb": tg_tb,
        "so_truy_cap": so_truy_cap,
        "so_nguoi_dung": so_nguoi_dung,
        "luot_dien_form": {
            "columns": rows_luot_dien_form,
            "data": luot_dien_form
        },
    }


def calc_so_nguoi_truy_cap_hien_tai():
    qr_truy_cap_hien_tai = f"""
    SELECT COUNT(ip) AS current_active_users
    FROM `tabCMS Session`
    WHERE active = 1
    AND time_out IS NOT NULL
    AND time_out >= NOW() - INTERVAL 30 MINUTE
    """
    return frappe.db.sql(qr_truy_cap_hien_tai, as_dict=1)[
        0]['current_active_users']


def calc_so_nguoi_truy_cap_30p_qua():
    qr_truy_cap_30p = f"""
    SELECT COUNT(DISTINCT ip) AS users_last_30_minutes
    FROM `tabCMS Session`
    WHERE time_out IS NOT NULL
    AND time_out >= NOW() - INTERVAL 30 MINUTE
    """
    return frappe.db.sql(qr_truy_cap_30p, as_dict=1)[
        0]['users_last_30_minutes']


@frappe.whitelist()
def report_dashboard(time_range_start=None, time_range_end=None, **kwargs):
    type_compare = kwargs.get('type_compare', None)

    today = datetime.now().date()
    if not time_range_start:
        start = today.strftime('%Y-%m-%d')
        end = start
        time_range_start = f"{start},{end}"
    if not time_range_end:
        start = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        end = start
        time_range_end = f"{start},{end}"

    truy_cap_hien_tai = calc_so_nguoi_truy_cap_hien_tai()
    truy_cap_30p = calc_so_nguoi_truy_cap_30p_qua()

    ls_time = time_range_start.split(',')
    time_start = ls_time[0]
    time_end = ls_time[1]
    ls_time = time_range_end.split(',')
    time_start1 = ls_time[0]
    time_end1 = ls_time[1]

    # time range start
    rp_range_start = calc_summary_report(time_start, time_end)

    # label legend in chart
    if time_start != time_end:
        str_range_start = (datetime.strptime(
            time_start, '%Y-%m-%d')).strftime('%d/%m/%Y') + ' - ' + (datetime.strptime(
                time_end, '%Y-%m-%d')).strftime('%d/%m/%Y')
        str_range_end = (datetime.strptime(
            time_start1, '%Y-%m-%d')).strftime('%d/%m/%Y') + ' - ' + (datetime.strptime(
                time_end1, '%Y-%m-%d')).strftime('%d/%m/%Y')
    else:
        str_range_start = (datetime.strptime(
            time_start, '%Y-%m-%d')).strftime('%d/%m/%Y')
        str_range_end = (datetime.strptime(
            time_start1, '%Y-%m-%d')).strftime('%d/%m/%Y')
    if type_compare != 'khong_so_sanh':
        rp_range_start['luot_truy_cap']['rows'] = [
            str_range_start, str_range_end]
        rp_range_start['luot_dien_form']['rows'] = [
            str_range_start, str_range_end]
    else:
        rp_range_start['luot_truy_cap']['rows'] = [
            str_range_start]
        rp_range_start['luot_dien_form']['rows'] = [
            str_range_start]

    te = (datetime.strptime(
        time_end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    trang_xem_nhieu = calc_trang_xem_nhieu_nhat(time_start, te)

    trang_xem_nhieu_truoc = {}
    if type_compare != 'khong_so_sanh':
        # time range end
        rp_range_end = calc_summary_report(time_start1, time_end1)
        # trang_xem_nhieu_truoc
        te = (datetime.strptime(
            time_end1, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        trang_xem_nhieu_truoc = calc_trang_xem_nhieu_nhat_ky_truoc(
            time_start1, te, trang_xem_nhieu.get('rows'))

    return {
        'rp_range_start': rp_range_start,
        'rp_range_end': rp_range_end if type_compare != 'khong_so_sanh' else None,
        'truy_cap_hien_tai': truy_cap_hien_tai,
        'truy_cap_30p': truy_cap_30p,
        'trang_xem_nhieu': trang_xem_nhieu,
        'trang_xem_nhieu_truoc': trang_xem_nhieu_truoc,
        'period': [str_range_start, str_range_end]
    }
