// Copyright (c) 2022, Tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Menu", {
  refresh: function (frm) {
    if (frm.doc.__unsaved) {
      frm.set_value("__newname", "SYS-M-");
    }
  },
  is_template: function (frm) {
    if (frm.doc.__unsaved) {
      if (frm.doc.is_template == 1) {
        frm.set_value("__newname", "SYS-M-");
      } else {
        frm.set_value("__newname", "US-M-");
      }
    }
  },
});

frappe.ui.form.on("Menus Item", {
  form_render: function (frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    if (item.is_mega_menu) {
      //   $(`[data-name="${cdn}"] [data-fieldname="mega_m_col_index"]`).hide();
      //   $(`[data-name="${cdn}"] [data-fieldname="parent_menu"]`).hide();
    }
    if (item.parent_menu) {
      //   $(`[data-name="${cdn}"] [data-fieldname="is_mega_menu"]`).hide();
      //   $(`[data-name="${cdn}"] [data-fieldname="no_of_column"]`).hide();
      //   $(`[data-name="${cdn}"] [data-fieldname="mega_m_col_index"]`).hide();
      cur_frm.doc.menus.map((res) => {
        if (res.menu_label == item.parent_menu) {
          if (res.is_mega_menu) {
            $(
              `[data-name="${cdn}"] [data-fieldname="mega_m_col_index"]`
            ).show();
          }
        }
      });
    }
  },
  is_mega_menu(frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    if (item.is_mega_menu) {
      item.parent_menu = "";
      item.mega_m_col_index = "";
      $(`[data-name="${cdn}"] [data-fieldname="parent_menu"]`).hide();
      $(`[data-name="${cdn}"] [data-fieldname="mega_m_col_index"]`).hide();
      refresh_field("menu");
    } else {
      $(`[data-name="${cdn}"] [data-fieldname="parent_menu"]`).show();
      $(`[data-name="${cdn}"] [data-fieldname="mega_m_col_index"]`).show();
    }
  },
  parent_menu(frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    if (item.parent_menu) {
      $(`[data-name="${cdn}"] [data-fieldname="mega_m_col_index"]`).show();
      $(`[data-name="${cdn}"] [data-fieldname="is_mega_menu"]`).hide();
      $(`[data-name="${cdn}"] [data-fieldname="no_of_column"]`).hide();
      item.is_mega_menu = 0;
      item.no_of_column = 0;
      refresh_field("menu");
    } else {
      $(`[data-name="${cdn}"] [data-fieldname="is_mega_menu"]`).show();
      $(`[data-name="${cdn}"] [data-fieldname="no_of_column"]`).show();
    }
  },
  mega_m_col_index(frm, cdt, cdn) {
    let item = locals[cdt][cdn];
    cur_frm.doc.menus.map((res) => {
      if (res.menu_label == item.parent_menu) {
        if (item.mega_m_col_index > res.no_of_column) {
          frappe.msgprint(
            `Index value can't be greater than mega menu columns`
          );
          item.mega_m_col_index = 0;
          refresh_field("menu");
        }
      }
    });
  },
});
