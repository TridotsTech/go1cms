import frappe
from frappe import _


@frappe.whitelist()
def get_menu_suggest():
    web_edit = frappe.db.get_value('MBW Client Website', {"edit": 1}, ['name'])
    if web_edit:
        menus = frappe.db.get_all("Menu", filters={"id_client_website": web_edit}, fields=[
            'name', 'id_parent_copy'
        ])
        menus_name = []

        for m in menus:
            menus_name.append(m.name)
            if m.id_parent_copy:
                menus_name.append(m.id_parent_copy)

        menus_item_suggest = frappe.db.get_all("Menus Item", filters={"parent": ('IN', menus_name), "parentfield": "menus"}, fields=[
            'menu_label', 'redirect_url'
        ], order_by="idx")
        menu_suggest = []
        for m in menus_item_suggest:
            if not next((item for item in menu_suggest if item["redirect_url"] == m.redirect_url), None):
                menu_suggest.append(m)
        return menu_suggest
    return []


@frappe.whitelist()
def get_menu(name):
    Menu = frappe.qb.DocType("Menu")
    query = (
        frappe.qb.from_(Menu)
        .select("*")
        .where(Menu.name == name)
    ).limit(1)

    menu = query.run(as_dict=True)
    if not len(menu):
        frappe.throw(_("Menu not found"), frappe.DoesNotExistError)
    menu = menu.pop()

    menus = frappe.db.get_all("Menus Item", filters={"parent": name, "parentfield": "menus"}, fields=[
        'name', 'menu_label', 'menu_id', 'parent_menu', 'is_mega_menu', 'no_of_column', 'mega_m_col_index', 'redirect_url', 'position', 'idx'
    ], order_by="idx")
    menu['menus'] = menus
    return menu


@frappe.whitelist()
def create_menu(data):
    title = data.get('title')
    if not title:
        frappe.throw(_("Tên menu không được để trống"))

    # init menu
    web_edit = frappe.get_last_doc('MBW Client Website', filters={"edit": 1})
    doc_new = frappe.new_doc('Menu')
    doc_new.title = title
    if web_edit:
        doc_new.id_client_website = web_edit.name
    doc_new.insert()

    for menu in data.get('menus'):
        data_update = {
            'menu_label': menu.get('menu_label'),
            'parent_menu': menu.get('parent_menu'),
            'is_mega_menu': menu.get('is_mega_menu') or 0,
            'no_of_column': menu.get('no_of_column') or 1,
            'mega_m_col_index': menu.get('mega_m_col_index') or 1,
            'redirect_url': menu.get('redirect_url'),
            'position': menu.get('position') or "Left",
            'idx': menu.get('idx'),
            'menu_id': menu.get('menu_id')
        }

        new_menu_it = frappe.new_doc('Menus Item')
        new_menu_it.parent = doc_new.name
        new_menu_it.parentfield = "menus"
        new_menu_it.parenttype = "Menu"
        new_menu_it.insert()

        # update menu item
        frappe.db.set_value('Menus Item', new_menu_it.name, data_update)

    result = {'name': doc_new.name}
    return result


@frappe.whitelist()
def update_menu(data):
    doc_name = data.get('name')
    title = data.get('title')
    if not frappe.db.exists("Menu", doc_name):
        frappe.throw(_("Menu not found"), frappe.DoesNotExistError)

    if not title:
        frappe.throw(_("Tên menu không được để trống"))

    doc = frappe.get_doc('Menu', doc_name)

    menus = frappe.db.get_all("Menus Item", filters={"parent": doc_name, "parentfield": "menus"}, fields=[
        'name', 'menu_label', 'menu_id', 'parent_menu', 'is_mega_menu', 'no_of_column', 'mega_m_col_index', 'redirect_url', 'position', 'idx'
    ], order_by="idx")

    # delete menu not found
    for menu in menus:
        if not next((item for item in data.get('menus') if item.get('name') == menu.name), None):
            frappe.delete_doc('Menus Item', menu.name)

    for menu in data.get('menus'):
        menu_name = menu.get('name')
        data_update = {
            'menu_label': menu.get('menu_label'),
            'parent_menu': menu.get('parent_menu'),
            'is_mega_menu': menu.get('is_mega_menu') or 0,
            'no_of_column': menu.get('no_of_column') or 1,
            'mega_m_col_index': menu.get('mega_m_col_index') or 1,
            'redirect_url': menu.get('redirect_url'),
            'position': menu.get('position') or "Left",
            'idx': menu.get('idx'),
            'menu_id': menu.get('menu_id')
        }

        if not menu_name:
            new_menu_it = frappe.new_doc('Menus Item')
            new_menu_it.parent = doc.name
            new_menu_it.parentfield = "menus"
            new_menu_it.parenttype = "Menu"
            new_menu_it.insert()
            menu_name = new_menu_it.name
        # update menu item
        frappe.db.set_value('Menus Item', menu_name, data_update)

    doc.reload()
    doc.title = title
    doc.save()

    result = {'name': doc.name}
    return result


@frappe.whitelist()
def delete_menu(name):
    try:
        if not frappe.db.exists("Menu", name):
            frappe.throw(_("Menu not found"), frappe.DoesNotExistError)

        frappe.delete_doc('Menu', name)
        result = {'name': name}
        return result
    except Exception as ex:
        frappe.clear_last_message()
        if type(ex) == frappe.LinkExistsError:
            frappe.throw(_("Menu này đã được liên kết, không thể xóa."))
        elif type(ex) == frappe.DoesNotExistError:
            frappe.throw(str(ex), type(ex))
        else:
            frappe.throw('Lỗi hệ thống')
